"""Bounded OpenAI thesis compiler using Responses API strict JSON Schema output."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import Condition, Evaluation, Event, Thesis


ALLOWED_FIELDS = {
    "total_premium", "total_size", "underlying_price", "total_ask_premium", "total_bid_premium",
    "has_sweep", "has_multileg", "has_singleleg",
}
OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "ticker": {"type": "string"},
        "statement": {"type": "string"},
        "summary": {"type": "string"},
        "conditions": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "properties": {
                "field": {"type": "string", "enum": sorted(ALLOWED_FIELDS)},
                "comparator": {"type": "string", "enum": ["gte", "gt", "lte", "lt", "eq"]},
                "threshold": {"type": ["number", "string", "boolean"]},
                "kind": {"type": "string", "enum": ["support", "weaken", "invalidate"]},
                "description": {"type": "string"},
            },
            "required": ["field", "comparator", "threshold", "kind", "description"],
        }},
        "required_fields": {"type": "array", "items": {"type": "string", "enum": sorted(ALLOWED_FIELDS)}},
        "freshness_seconds": {"type": "integer"},
        "uncertainties": {"type": "array", "items": {"type": "string"}},
        "evidence_refs": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["ticker", "statement", "summary", "conditions", "required_fields", "freshness_seconds", "uncertainties", "evidence_refs"],
}


class ThesisCompileError(RuntimeError):
    """Safe, non-secret compiler failure; contains no raw API response."""

    def __init__(self, message: str, *, status: int | None = None, category: str | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.category = category


@dataclass(frozen=True)
class ThesisProposal:
    thesis: Thesis
    summary: str
    uncertainties: tuple[str, ...]
    evidence_refs: tuple[str, ...] = ()


class ThesisCompiler:
    def __init__(self, *, api_key: str | None = None, model: str | None = None, timeout: float = 30.0) -> None:
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self._api_key:
            raise ThesisCompileError("Set OPENAI_API_KEY in the process environment to compile a thesis")
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-6-astra")
        self.timeout = timeout

    @staticmethod
    def _validate(
        data: Any, *, thesis_id: str, version: int, allowed_evidence_refs: set[str] | None = None,
        expected_ticker: str | None = None,
    ) -> ThesisProposal:
        if not isinstance(data, dict):
            raise ThesisCompileError("Model output was not a JSON object")
        ticker = data.get("ticker")
        if not isinstance(ticker, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9.]{0,9}", ticker):
            raise ThesisCompileError("Model proposed an invalid ticker")
        if expected_ticker is not None and ticker.upper() != expected_ticker.upper():
            raise ThesisCompileError("Model ticker did not match the requested ticker")
        conditions_data = data.get("conditions")
        if not isinstance(conditions_data, list) or not conditions_data:
            raise ThesisCompileError("Model must propose at least one deterministic condition")
        conditions: list[Condition] = []
        for index, item in enumerate(conditions_data):
            if not isinstance(item, dict) or item.get("field") not in ALLOWED_FIELDS:
                raise ThesisCompileError("Model proposed a field that live normalization does not support")
            threshold = item.get("threshold")
            if item["field"].startswith("has_"):
                if not isinstance(threshold, bool) or item.get("comparator") != "eq":
                    raise ThesisCompileError("Boolean flags require an equality predicate")
            elif isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
                raise ThesisCompileError("Numeric fields require a numeric threshold")
            elif abs(float(threshold)) > 1e15:
                raise ThesisCompileError("Threshold is outside the supported range")
            conditions.append(Condition(
                id=f"c{index + 1}", field=item["field"], comparator=item["comparator"],
                threshold=threshold, kind=item["kind"], description=str(item["description"])[:240],
            ))
        required = data.get("required_fields")
        if not isinstance(required, list) or any(field not in ALLOWED_FIELDS for field in required):
            raise ThesisCompileError("Model proposed unsupported required fields")
        freshness = data.get("freshness_seconds")
        if not isinstance(freshness, int) or isinstance(freshness, bool) or not 60 <= freshness <= 86400:
            raise ThesisCompileError("Freshness must be between 60 seconds and 24 hours")
        statement, summary = data.get("statement"), data.get("summary")
        uncertainties = data.get("uncertainties")
        if not isinstance(statement, str) or not statement.strip() or not isinstance(summary, str):
            raise ThesisCompileError("Model output is missing a statement or summary")
        if not isinstance(uncertainties, list) or any(not isinstance(x, str) for x in uncertainties):
            raise ThesisCompileError("Uncertainty field was malformed")
        evidence_refs = data.get("evidence_refs")
        allowed_refs = allowed_evidence_refs or set()
        if not isinstance(evidence_refs, list) or any(
            not isinstance(ref, str) or ref not in allowed_refs for ref in evidence_refs
        ):
            raise ThesisCompileError("Model cited evidence that was not supplied to the compiler")
        thesis = Thesis(
            id=thesis_id, version=version, ticker=ticker.upper(), statement=statement[:500].strip(),
            conditions=tuple(conditions), required_fields=tuple(dict.fromkeys(required)),
            freshness_seconds=freshness, status="draft",
        )
        return ThesisProposal(
            thesis, summary[:500], tuple(x[:300] for x in uncertainties[:10]),
            tuple(dict.fromkeys(evidence_refs)),
        )

    @staticmethod
    def _evidence_context(
        events: Iterable[Event], evaluation: Evaluation | None,
    ) -> tuple[dict[str, Any], set[str]]:
        event_list = list(events)
        allowed = set(evaluation.event_ids) if evaluation is not None else {
            event.source_id for event in event_list
        }
        event_records = []
        for event in event_list:
            if event.source_id not in allowed:
                continue
            normalized_fields = {
                key: value for key, value in event.fields.items()
                if key in ALLOWED_FIELDS and isinstance(value, (str, int, float, bool))
            }
            event_records.append({
                "source_id": event.source_id,
                "ticker": event.ticker.upper(),
                "event_time": event.event_time.isoformat(),
                "fields": normalized_fields,
                "complete": event.complete,
            })
        predicates = [{
            "condition_id": item.condition_id, "kind": item.kind, "matched": item.matched,
            "observed": item.observed, "threshold": item.threshold,
            "event_ids": list(item.event_ids), "reason": item.reason,
        } for item in evaluation.predicates] if evaluation is not None else []
        context = {
            "evaluation_status": evaluation.status if evaluation is not None else "not_evaluated",
            "evaluated_at": evaluation.evaluated_at.isoformat() if evaluation is not None else None,
            "event_ids": list(evaluation.event_ids) if evaluation is not None else sorted(allowed),
            "predicates": predicates,
            "events": event_records,
            "mode": evaluation.mode if evaluation is not None else (
                "live" if any(event.mode == "live" for event in event_list) else "replay"
            ),
        }
        return context, allowed

    def compile(
        self, user_statement: str, *, thesis_id: str = "draft", version: int = 1,
        expected_ticker: str | None = None,
        evaluation: Evaluation | None = None, events: Iterable[Event] = (),
    ) -> ThesisProposal:
        if not user_statement.strip() or len(user_statement) > 3000:
            raise ValueError("statement must contain 1 to 3000 characters")
        evidence_context: dict[str, Any] | None = None
        allowed_evidence_refs: set[str] = set()
        event_list = list(events)
        if evaluation is not None or event_list:
            evidence_context, allowed_evidence_refs = self._evidence_context(event_list, evaluation)
        request_body = {
            "model": self.model,
            "store": False,
            "max_output_tokens": 800,
            "input": [
                {"role": "system", "content": (
                    "Convert the user's market thesis into a DRAFT rule proposal for observable Unusual Whales Flow Alert data. "
                    "Do not predict prices, recommend trades, or invent observations. Use only supported fields and explicit "
                    "thresholds justified by the user's statement. If no defensible threshold exists, return a conservative "
                    "proposal and explain uncertainty. Conditions are deterministic predicates, not conclusions about the market. "
                    "When evidence context is supplied, explain only its listed facts, cite only its event IDs, "
                    "and never infer a buy/sell direction from options flow alone. The underlying_price field is the "
                    "price attached to that alert at its event time, not a current quote. The result is always an unactivated draft."
                )},
                {"role": "user", "content": json.dumps({
                    "user_statement": user_statement,
                    "deterministic_evidence": evidence_context,
                }, sort_keys=True, separators=(",", ":"))},
            ],
            "text": {"format": {"type": "json_schema", "name": "thesis_proposal", "strict": True, "schema": OUTPUT_SCHEMA}},
        }
        request = Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(request_body).encode("utf-8"),
            headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                response_obj = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            category = f"http_{error.code}"
            if error.code == 429:
                try:
                    error_obj = json.loads(error.read().decode("utf-8"))
                    err = error_obj.get("error", {}) if isinstance(error_obj, dict) else {}
                    safe_code = err.get("code") if isinstance(err, dict) else None
                    safe_codes = {
                        "insufficient_quota", "credit_balance_exhausted", "rate_limit_exceeded",
                        "rate_limit_error", "slow_down", "usage_limit_exceeded",
                        "organization_spend_limit_exceeded", "project_spend_limit_exceeded",
                        "organization_usage_limit_exceeded",
                    }
                    if isinstance(safe_code, str) and safe_code in safe_codes:
                        category = safe_code
                    elif not isinstance(safe_code, str):
                        category = "rate_limit_or_quota"
                except (ValueError, UnicodeDecodeError):
                    pass
            raise ThesisCompileError(
                f"OpenAI Responses request failed with HTTP {error.code}",
                status=error.code, category=category,
            ) from None
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise ThesisCompileError(
                f"OpenAI Responses request failed: {type(error).__name__}", category=type(error).__name__
            ) from None
        if not isinstance(response_obj, dict):
            raise ThesisCompileError("Model response was not a JSON object")
        if response_obj.get("status") == "incomplete":
            raise ThesisCompileError("Model response was incomplete")
        texts: list[str] = []
        for output in response_obj.get("output", []):
            for item in output.get("content", []):
                if item.get("type") == "refusal":
                    raise ThesisCompileError("Model refused to compile this statement")
                if item.get("type") == "output_text" and isinstance(item.get("text"), str):
                    texts.append(item["text"])
        if not texts:
            raise ThesisCompileError("Model returned no structured output")
        try:
            decoded = json.loads("".join(texts))
        except json.JSONDecodeError:
            raise ThesisCompileError("Model returned invalid structured output") from None
        return self._validate(
            decoded, thesis_id=thesis_id, version=version,
            allowed_evidence_refs=allowed_evidence_refs,
            expected_ticker=expected_ticker,
        )

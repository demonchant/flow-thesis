"""Normalize UW Flow Alert responses and poll them into the local thesis ledger."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from .models import Event, Thesis
from .store import LedgerStore
from .uw_api import UWAPIError, UWClient


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        if isinstance(value, str):
            value = value.strip().replace(",", "").replace("$", "")
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return result if result == result and abs(result) != float("inf") else None


def _timestamp(value: Any) -> datetime | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (ValueError, OSError, OverflowError):
            return None
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed
        except ValueError:
            return None
    return None


def normalize_flow_alerts(payload: Any, *, received_at: datetime | None = None) -> list[Event]:
    """Map only documented, useful values into a stable domain event.

    Unknown fields are ignored. Malformed rows are omitted instead of being
    represented as valid observations, so they cannot support a thesis.
    """
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise ValueError("UW Flow Alerts response must contain a data array")
    received = received_at or datetime.now(timezone.utc)
    if received.tzinfo is None:
        raise ValueError("received_at must include a timezone")
    normalized: list[Event] = []
    for item in payload["data"]:
        if not isinstance(item, dict):
            continue
        ticker = item.get("ticker") or item.get("ticker_symbol")
        event_time = _timestamp(item.get("created_at"))
        if not isinstance(ticker, str) or not ticker.strip() or event_time is None:
            continue
        ticker = ticker.strip().upper()
        fields: dict[str, Any] = {}
        aliases = {
            "total_premium": ("total_premium", "premium"),
            "total_size": ("total_size", "size"),
            "underlying_price": ("underlying_price", "stock_price"),
            "total_ask_premium": ("total_ask_side_prem", "total_ask_premium", "ask_premium"),
            "total_bid_premium": ("total_bid_side_prem", "total_bid_premium", "bid_premium"),
        }
        for target, keys in aliases.items():
            for key in keys:
                parsed = _number(item.get(key))
                if parsed is not None:
                    fields[target] = parsed
                    break
        for name in ("has_sweep", "has_multileg", "has_singleleg"):
            if isinstance(item.get(name), bool):
                fields[name] = item[name]
        for name in ("alert_rule",):
            if isinstance(item.get(name), str):
                fields[name] = item[name]
        explicit_id = item.get("id") or item.get("alert_id")
        if explicit_id is not None:
            source_id = str(explicit_id)
        else:
            canonical = json.dumps(item, sort_keys=True, separators=(",", ":"), default=str)
            source_id = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        normalized.append(Event(
            source="unusualwhales.flow_alerts", source_id=source_id, ticker=ticker,
            event_time=event_time, received_at=received, kind="flow_alert", fields=fields,
            complete=bool(fields), mode="live",
        ))
    return normalized


class FlowAlertPoller:
    """Single-process poller. Call poll_once on a timer; no background thread is hidden."""

    def __init__(self, client: UWClient, store: LedgerStore, *, limit: int = 100) -> None:
        if not 1 <= limit <= 200:
            raise ValueError("limit must be from 1 to 200")
        self.client, self.store, self.limit = client, store, limit

    def poll_once(self, thesis: Thesis, *, all_opening: bool = False) -> dict[str, Any]:
        cursor = self.store.poll_cursor(thesis.id, thesis.ticker)
        params: dict[str, Any] = {
            "ticker_symbol": thesis.ticker.upper(), "limit": self.limit,
            "all_opening": str(all_opening).lower(),
        }
        if cursor:
            params["newer_than"] = cursor
        response = self.client.flow_alerts(params)
        events = normalize_flow_alerts(response.body)
        matching = [e for e in events if e.ticker == thesis.ticker.upper()]
        inserted = self.store.append_events(matching)
        # A full page is potentially truncated. Keep the prior cursor so next
        # poll can safely overlap/retrieve the boundary again.
        raw_rows = response.body.get("data", []) if isinstance(response.body, dict) else []
        truncated = len(raw_rows) >= self.limit
        if matching and not truncated:
            latest = max(matching, key=lambda event: event.event_time)
            self.store.set_poll_cursor(thesis.id, thesis.ticker, latest.event_time.isoformat())
        events_for_thesis = self.store.load_events()
        from .engine import evaluate_snapshot
        evaluation = evaluate_snapshot(thesis, events_for_thesis)
        previous = self.store.latest_status(thesis.id)
        recorded = self.store.record_evaluation(evaluation, previous)
        return {
            "http_status": response.status,
            "received": len(raw_rows),
            "normalized": len(matching),
            "inserted": inserted,
            "possibly_truncated": truncated,
            "evaluation": evaluation,
            "evaluation_recorded": recorded,
        }


def classify_uw_error(error: UWAPIError) -> str:
    if error.status == 401:
        return "unauthorized"
    if error.status == 403:
        return "not_entitled_or_forbidden"
    if error.status == 429:
        return "rate_limited"
    if error.status == 404:
        return "route_or_resource_not_found"
    return "transient_or_upstream_failure" if error.retryable else "request_rejected"

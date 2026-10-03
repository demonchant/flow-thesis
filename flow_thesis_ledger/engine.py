"""Pure, repeatable thesis evaluation and point-in-time replay."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Iterable

from .models import Condition, Evaluation, Event, PredicateResult, Thesis, ThesisStatus


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _matches(observed: Any, condition: Condition) -> bool:
    if condition.comparator == "eq":
        return observed == condition.threshold
    if isinstance(observed, bool) or isinstance(condition.threshold, bool):
        raise TypeError("ordered comparisons do not accept boolean values")
    left, right = float(observed), float(condition.threshold)
    return {
        "gte": left >= right,
        "gt": left > right,
        "lte": left <= right,
        "lt": left < right,
    }[condition.comparator]


def _predicate(condition: Condition, events: list[Event]) -> PredicateResult:
    available = [(event, event.fields[condition.field]) for event in events if condition.field in event.fields]
    if not available:
        return PredicateResult(
            condition.id, condition.kind, None, None, condition.threshold, (), "required field absent"
        )
    # The newest event-time observation is used; received time is only a tie-breaker.
    event, observed = max(available, key=lambda pair: (pair[0].event_time, pair[0].received_at))
    try:
        matched = _matches(observed, condition)
    except (TypeError, ValueError, OverflowError):
        return PredicateResult(
            condition.id, condition.kind, None, observed, condition.threshold,
            (event.source_id,), "value is not comparable to the configured threshold"
        )
    return PredicateResult(condition.id, condition.kind, matched, observed, condition.threshold, (event.source_id,))


def evaluate_snapshot(
    thesis: Thesis,
    events: Iterable[Event],
    *,
    evaluated_at: datetime | None = None,
) -> Evaluation:
    """Evaluate one immutable observation set; missing/stale evidence fails closed."""
    instant = evaluated_at or datetime.now(timezone.utc)
    if instant.tzinfo is None:
        raise ValueError("evaluated_at must include a timezone")
    all_events = [event for event in events if event.ticker.upper() == thesis.ticker.upper()]
    # Point-in-time guard: future events cannot affect an earlier evaluation.
    selected = [event for event in all_events if event.event_time <= instant]
    selected.sort(key=lambda event: (event.event_time, event.source_id))
    unique: dict[tuple[str, str], Event] = {}
    for event in selected:
        unique[(event.source, event.source_id)] = event
    observations = list(unique.values())
    ids = tuple(event.source_id for event in observations)
    modes = {event.mode for event in observations}
    mode = "synthetic" if "synthetic" in modes else "live" if modes == {"live"} else "replay"
    input_material = {
        "thesis_id": thesis.id,
        "thesis_version": thesis.version,
        "ticker": thesis.ticker.upper(),
        "conditions": [condition.__dict__ for condition in thesis.conditions],
        "required_fields": thesis.required_fields,
        "freshness_seconds": thesis.freshness_seconds,
        "evaluated_at": instant.isoformat(),
        "events": [event.as_dict() for event in observations],
    }
    input_hash = _canonical_hash(input_material)
    reasons: list[str] = []
    fresh_events = [
        event for event in observations
        if 0 <= (instant - event.event_time).total_seconds() <= thesis.freshness_seconds
    ]
    if not fresh_events:
        reasons.append("no fresh observations within the configured freshness window")
    incomplete = [event for event in fresh_events if not event.complete]
    if incomplete:
        reasons.append("one or more fresh observations are marked partial")
    missing = [field for field in thesis.required_fields if not any(field in e.fields for e in fresh_events)]
    if missing:
        reasons.append("missing required fields: " + ", ".join(sorted(missing)))
    predicates = tuple(_predicate(condition, fresh_events) for condition in thesis.conditions)
    unresolved = [predicate for predicate in predicates if predicate.matched is None]
    if unresolved:
        reasons.extend(f"condition {item.condition_id}: {item.reason}" for item in unresolved)
    if reasons:
        status: ThesisStatus = "indeterminate"
    elif any(item.kind == "invalidate" and item.matched for item in predicates):
        status = "invalidated"
    elif any(item.kind == "weaken" and item.matched for item in predicates):
        status = "weakened"
    elif any(item.kind == "support" and item.matched for item in predicates):
        status = "supported"
    else:
        status = "monitoring"
    output_material = {
        "thesis_id": thesis.id,
        "version": thesis.version,
        "status": status,
        "evaluated_at": instant.isoformat(),
        "event_ids": ids,
        "predicates": [item.__dict__ for item in predicates],
        "reasons": reasons,
        "input_hash": input_hash,
        "mode": mode,
    }
    return Evaluation(
        thesis.id, thesis.version, status, instant, ids, predicates, tuple(reasons), input_hash,
        _canonical_hash(output_material), mode
    )


def replay(thesis: Thesis, events: Iterable[Event]) -> list[Evaluation]:
    """Evaluate after each unique event in event-time order for reproducible replay."""
    unique: dict[tuple[str, str], Event] = {}
    for event in events:
        if event.ticker.upper() == thesis.ticker.upper():
            unique[(event.source, event.source_id)] = event
    ordered = sorted(unique.values(), key=lambda event: (event.event_time, event.source_id))
    return [
        evaluate_snapshot(thesis, ordered[: index + 1], evaluated_at=event.event_time)
        for index, event in enumerate(ordered)
    ]

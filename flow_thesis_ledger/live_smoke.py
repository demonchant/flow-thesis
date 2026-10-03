"""One-shot live contract + normalize/persist/evaluate smoke test.

Run from a shell that already has UW_API_KEY. Output contains route statuses,
JSON key names/types, counts and smoke state only. No API values are printed or
persisted beyond the process; SQLite is an in-memory database.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from .models import Condition, Thesis
from .store import LedgerStore
from .uw_api import UWAPIError, UWClient
from .uw_ingest import FlowAlertPoller, normalize_flow_alerts
from .verify_uw import _safe_shape


def _emit(value: dict[str, object]) -> None:
    print(json.dumps(value, sort_keys=True))


def main() -> None:
    try:
        client = UWClient(timeout=20, retries=1)
    except UWAPIError as error:
        _emit({"stage": "configuration", "status": "blocked", "reason": str(error)})
        raise SystemExit(1) from None

    try:
        first = client.flow_alerts({"limit": 1, "all_opening": "false"})
    except UWAPIError as error:
        _emit({"stage": "initial_fetch", "http_status": error.status, "access": error.status or "request_failed"})
        raise SystemExit(1) from None
    rows = first.body.get("data", []) if isinstance(first.body, dict) else []
    _emit({
        "stage": "initial_fetch", "endpoint": "GET /api/option-trades/flow-alerts",
        "http_status": first.status,
        "response_shape": "data array" if isinstance(first.body, dict) and isinstance(first.body.get("data"), list) else "unexpected",
        "row_count": len(rows) if isinstance(rows, list) else 0,
        "first_row_shape": _safe_shape(rows[0]) if isinstance(rows, list) and rows else None,
    })
    if not rows:
        _emit({"stage": "normalization", "status": "no_rows_to_normalize"})
        raise SystemExit(2)

    try:
        first_events = normalize_flow_alerts(first.body)
    except ValueError:
        _emit({"stage": "normalization", "status": "response_contract_mismatch"})
        raise SystemExit(2) from None
    _emit({
        "stage": "normalization", "normalized_count": len(first_events),
        "normalized_fields": sorted(first_events[0].fields) if first_events else [],
        "status": "ok" if first_events else "no_usable_events",
    })
    if not first_events:
        raise SystemExit(2)

    # Verify detail shape without exposing the identifier or any returned values.
    first_raw = rows[0] if isinstance(rows[0], dict) else {}
    alert_id = first_raw.get("id") or first_raw.get("alert_id")
    if alert_id is not None:
        try:
            detail = client.flow_alert(str(alert_id))
            body = detail.body
            _emit({
                "stage": "detail_fetch", "endpoint": "GET /api/option-trades/flow-alerts/{id}",
                "http_status": detail.status,
                "top_level_fields": sorted(str(key) for key in body) if isinstance(body, dict) else [],
                "alert_shape": _safe_shape(body.get("alert")) if isinstance(body, dict) and "alert" in body else None,
                "first_trade_shape": _safe_shape(body["trades"][0]) if isinstance(body, dict) and isinstance(body.get("trades"), list) and body["trades"] else None,
            })
        except UWAPIError as error:
            _emit({"stage": "detail_fetch", "http_status": error.status, "status": "failed"})

    event = first_events[0]
    numeric_field = next((name for name in (
        "total_premium", "total_size", "total_ask_premium", "total_bid_premium",
    ) if name in event.fields), None)
    bool_field = next((name for name in ("has_sweep", "has_multileg", "has_singleleg") if name in event.fields), None)
    if numeric_field:
        condition = Condition("smoke-rule", numeric_field, "gte", 0, "support", "Smoke check only")
        required = (numeric_field,)
    elif bool_field:
        condition = Condition("smoke-rule", bool_field, "eq", True, "support", "Smoke check only")
        required = (bool_field,)
    else:
        condition = Condition("smoke-rule", "total_premium", "gte", 0, "support", "Smoke check only")
        required = ("total_premium",)
    thesis = Thesis(
        id="ephemeral-live-smoke", version=1, ticker=event.ticker,
        statement="Ephemeral ingestion smoke check; not a market thesis.", conditions=(condition,),
        required_fields=required, freshness_seconds=86_400, status="monitoring",
    )
    store = LedgerStore(":memory:")
    store.save_thesis(thesis, datetime.now(timezone.utc).isoformat())
    try:
        result = FlowAlertPoller(client, store, limit=5).poll_once(thesis, all_opening=False)
    except UWAPIError as error:
        _emit({"stage": "poll_and_evaluate", "http_status": error.status, "status": "failed"})
        raise SystemExit(3) from None
    evaluation = result["evaluation"]
    _emit({
        "stage": "poll_and_evaluate", "endpoint": "GET /api/option-trades/flow-alerts",
        "http_status": result["http_status"], "rows_received": result["received"],
        "events_normalized": result["normalized"], "events_persisted_in_memory": result["inserted"],
        "possibly_truncated": result["possibly_truncated"], "evaluation_state": evaluation.status,
        "mode": evaluation.mode, "smoke_only": True,
    })
    _emit({"stage": "cleanup", "status": "complete", "persistence": "memory_only"})


if __name__ == "__main__":
    main()

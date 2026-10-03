"""Read-only Flow Alerts poller for an explicitly reviewed thesis JSON draft."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from dataclasses import replace

from .engine import evaluate_snapshot
from .models import Condition, Thesis
from .store import LedgerStore
from .uw_api import UWAPIError, UWClient
from .uw_ingest import FlowAlertPoller, classify_uw_error


def load_thesis(path: Path) -> Thesis:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("thesis", payload)
    conditions = tuple(Condition(**condition) for condition in raw["conditions"])
    return Thesis(
        id=str(raw["id"]), version=int(raw["version"]), ticker=str(raw["ticker"]),
        statement=str(raw["statement"]), conditions=conditions,
        required_fields=tuple(raw.get("required_fields", [])),
        freshness_seconds=int(raw.get("freshness_seconds", 900)),
        status=str(raw.get("status", "draft")),
    )


def prepare_monitoring(thesis: Thesis, store: LedgerStore, *, approve: bool, now: str) -> Thesis:
    """Require explicit review for a draft and persist the monitoring approval."""
    if thesis.status == "draft":
        if store.is_activated(thesis.id, thesis.version):
            return replace(thesis, status="monitoring")
        if not approve:
            raise PermissionError("draft requires explicit --approve before read-only monitoring")
        activated = store.activate_thesis(thesis, human_approved=True, approved_at=now)
        return activated
    if thesis.status == "monitoring" and store.is_activated(thesis.id, thesis.version):
        return thesis
    raise PermissionError("thesis is not approved for monitoring")


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll UW Flow Alerts and evaluate a reviewed thesis")
    parser.add_argument("thesis", type=Path, help="Reviewed thesis JSON (draft from compile_thesis.py)")
    parser.add_argument("--db", type=Path, default=Path(".local/flow-thesis-ledger.sqlite3"))
    parser.add_argument("--interval", type=int, default=60, help="poll interval in seconds, minimum 30")
    parser.add_argument("--limit", type=int, default=100, help="page size (1-200)")
    parser.add_argument("--once", action="store_true", help="poll exactly once and exit")
    parser.add_argument("--all-opening", action="store_true", help="restrict to opening flow alerts")
    parser.add_argument("--approve", action="store_true", help="confirm review and activate read-only monitoring")
    args = parser.parse_args()
    if args.interval < 30:
        parser.error("--interval must be at least 30 seconds")
    thesis = load_thesis(args.thesis)
    store = LedgerStore(args.db)
    try:
        thesis = prepare_monitoring(
            thesis, store, approve=args.approve,
            now=datetime.now().astimezone().isoformat(),
        )
    except PermissionError as error:
        raise SystemExit(str(error)) from None
    store.save_thesis(thesis, datetime.now().astimezone().isoformat())
    try:
        poller = FlowAlertPoller(UWClient(), store, limit=args.limit)
    except UWAPIError as error:
        raise SystemExit(str(error)) from None
    print(f"Monitoring {thesis.ticker}: GET /api/option-trades/flow-alerts; local database only.")
    while True:
        try:
            result = poller.poll_once(thesis, all_opening=args.all_opening)
            evaluation = result["evaluation"]
            print(json.dumps({
                "http_status": result["http_status"], "received": result["received"],
                "normalized": result["normalized"], "inserted": result["inserted"],
                "possibly_truncated": result["possibly_truncated"],
                "state": evaluation.status, "reasons": evaluation.reasons,
                "input_hash": evaluation.input_hash, "output_hash": evaluation.output_hash,
            }, sort_keys=True))
        except UWAPIError as error:
            # Never print an upstream body, URL, request header, or credential.
            print(json.dumps({"http_status": error.status, "condition": classify_uw_error(error)}))
            if error.status in {401, 403}:
                raise SystemExit(1) from None
        except (ValueError, OSError, json.JSONDecodeError) as error:
            print(json.dumps({"local_error": type(error).__name__}))
        if args.once:
            return
        time.sleep(args.interval)


if __name__ == "__main__":
    main()

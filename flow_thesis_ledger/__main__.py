"""CLI for replaying an explicitly labeled JSON snapshot."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .engine import replay
from .models import Condition, Event, Thesis
from .store import LedgerStore


def _datetime(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timestamps must include a timezone, such as Z")
    return result


def load_snapshot(path: Path) -> tuple[Thesis, list[Event], str]:
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    thesis_data = payload["thesis"]
    conditions = tuple(Condition(**item) for item in thesis_data["conditions"])
    thesis = Thesis(
        id=thesis_data["id"],
        version=int(thesis_data["version"]),
        ticker=thesis_data["ticker"],
        statement=thesis_data["statement"],
        conditions=conditions,
        required_fields=tuple(thesis_data.get("required_fields", [])),
        freshness_seconds=int(thesis_data.get("freshness_seconds", 900)),
    )
    events = [
        Event(
            source=item["source"], source_id=item["source_id"], ticker=item["ticker"],
            event_time=_datetime(item["event_time"]), received_at=_datetime(item["received_at"]),
            kind=item["kind"], fields=item.get("fields", {}), complete=bool(item.get("complete", True)),
            mode=item.get("mode", "replay"),
        )
        for item in payload["events"]
    ]
    return thesis, events, payload.get("label", "unlabeled snapshot")


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay a Flow Thesis Ledger snapshot")
    parser.add_argument("snapshot", type=Path, help="JSON snapshot containing recorded observation data")
    parser.add_argument("--db", type=Path, help="optional SQLite path for local receipt persistence")
    args = parser.parse_args()
    thesis, events, label = load_snapshot(args.snapshot)
    results = replay(thesis, events)
    store = LedgerStore(args.db) if args.db else None
    if store:
        store.save_thesis(thesis, datetime.now().astimezone().isoformat())
        store.append_events(events)
    previous: str | None = None
    for result in results:
        if store:
            store.record_evaluation(result, previous)
        print(json.dumps({
            "label": label,
            "mode": result.mode,
            "evaluated_at": result.evaluated_at.isoformat(),
            "state": result.status,
            "event_ids": result.event_ids,
            "reasons": result.reasons,
            "predicates": [item.__dict__ for item in result.predicates],
            "input_hash": result.input_hash,
            "output_hash": result.output_hash,
        }, sort_keys=True, default=str))
        previous = result.status


if __name__ == "__main__":
    main()

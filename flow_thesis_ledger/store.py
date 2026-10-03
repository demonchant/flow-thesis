"""SQLite persistence for thesis versions and append-only evaluation receipts."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from datetime import datetime
import hashlib
import uuid
from dataclasses import replace

from .models import Evaluation, Event, Thesis


class LedgerStore:
    def __init__(self, path: str | Path = "flow-thesis-ledger.sqlite3") -> None:
        raw_path = str(path)
        self._uri = raw_path == ":memory:"
        self.path = f"file:flow-ledger-{uuid.uuid4().hex}?mode=memory&cache=shared" if self._uri else raw_path
        self._anchor = sqlite3.connect(self.path, uri=True) if self._uri else None
        if self.path != ":memory:":
            if not self._uri:
                Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, uri=self._uri)
        db.row_factory = sqlite3.Row
        return db

    def close(self) -> None:
        """Release the anchor connection that keeps a shared in-memory DB alive."""
        if self._anchor is not None:
            self._anchor.close()
            self._anchor = None

    def __enter__(self) -> "LedgerStore":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    @contextmanager
    def _db(self) -> Iterator[sqlite3.Connection]:
        db = self._connect()
        try:
            with db:
                yield db
        finally:
            db.close()

    def _initialize(self) -> None:
        with self._db() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("""CREATE TABLE IF NOT EXISTS thesis_versions (
                thesis_id TEXT NOT NULL, version INTEGER NOT NULL, ticker TEXT NOT NULL,
                statement TEXT NOT NULL, definition_json TEXT NOT NULL, created_at TEXT NOT NULL,
                PRIMARY KEY (thesis_id, version))""")
            db.execute("""CREATE TABLE IF NOT EXISTS evaluations (
                output_hash TEXT PRIMARY KEY, thesis_id TEXT NOT NULL, thesis_version INTEGER NOT NULL,
                evaluated_at TEXT NOT NULL, status TEXT NOT NULL, input_hash TEXT NOT NULL,
                receipt_json TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS event_versions (
                event_version_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL, source_id TEXT NOT NULL, payload_hash TEXT NOT NULL,
                event_time TEXT NOT NULL, received_at TEXT NOT NULL, ticker TEXT NOT NULL,
                event_json TEXT NOT NULL, UNIQUE(source, source_id, payload_hash))""")
            db.execute("""CREATE TABLE IF NOT EXISTS transitions (
                transition_id INTEGER PRIMARY KEY AUTOINCREMENT, thesis_id TEXT NOT NULL,
                thesis_version INTEGER NOT NULL, previous_status TEXT, next_status TEXT NOT NULL,
                evaluation_hash TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS poll_cursors (
                thesis_id TEXT NOT NULL, ticker TEXT NOT NULL, cursor TEXT NOT NULL,
                updated_at TEXT NOT NULL, PRIMARY KEY(thesis_id, ticker))""")
            db.execute("""CREATE TABLE IF NOT EXISTS thesis_activations (
                thesis_id TEXT NOT NULL, version INTEGER NOT NULL, approved_at TEXT NOT NULL,
                PRIMARY KEY(thesis_id, version))""")

    def poll_cursor(self, thesis_id: str, ticker: str) -> str | None:
        with self._db() as db:
            row = db.execute(
                "SELECT cursor FROM poll_cursors WHERE thesis_id = ? AND ticker = ?",
                (thesis_id, ticker.upper()),
            ).fetchone()
            return row["cursor"] if row else None

    def set_poll_cursor(self, thesis_id: str, ticker: str, cursor: str) -> None:
        """Advance the poll watermark only after its event page was persisted."""
        with self._db() as db:
            db.execute(
                "INSERT INTO poll_cursors VALUES (?, ?, ?, ?) "
                "ON CONFLICT(thesis_id, ticker) DO UPDATE SET cursor=excluded.cursor, "
                "updated_at=excluded.updated_at",
                (thesis_id, ticker.upper(), cursor, datetime.now().astimezone().isoformat()),
            )

    def save_thesis(self, thesis: Thesis, created_at: str) -> None:
        conditions = [condition.__dict__ for condition in thesis.conditions]
        definition = {
            "conditions": conditions,
            "required_fields": thesis.required_fields,
            "freshness_seconds": thesis.freshness_seconds,
        }
        with self._db() as db:
            db.execute(
                "INSERT OR IGNORE INTO thesis_versions VALUES (?, ?, ?, ?, ?, ?)",
                (thesis.id, thesis.version, thesis.ticker.upper(), thesis.statement,
                 json.dumps(definition, sort_keys=True), created_at),
            )

    def activate_thesis(self, thesis: Thesis, *, human_approved: bool, approved_at: str) -> Thesis:
        """Activate read-only monitoring only after explicit human approval."""
        if human_approved is not True:
            raise PermissionError("explicit human approval is required to activate monitoring")
        if thesis.status != "draft":
            raise ValueError("only a draft thesis can be activated")
        activated = replace(thesis, status="monitoring")
        with self._db() as db:
            conditions = [condition.__dict__ for condition in activated.conditions]
            definition = {
                "conditions": conditions,
                "required_fields": activated.required_fields,
                "freshness_seconds": activated.freshness_seconds,
            }
            db.execute(
                "INSERT OR IGNORE INTO thesis_versions VALUES (?, ?, ?, ?, ?, ?)",
                (activated.id, activated.version, activated.ticker.upper(), activated.statement,
                 json.dumps(definition, sort_keys=True), approved_at),
            )
            db.execute(
                "INSERT INTO thesis_activations VALUES (?, ?, ?) "
                "ON CONFLICT(thesis_id, version) DO NOTHING",
                (activated.id, activated.version, approved_at),
            )
        return activated

    def is_activated(self, thesis_id: str, version: int) -> bool:
        with self._db() as db:
            row = db.execute(
                "SELECT 1 FROM thesis_activations WHERE thesis_id = ? AND version = ?",
                (thesis_id, version),
            ).fetchone()
            return row is not None

    def append_events(self, events: list[Event]) -> int:
        """Persist local event snapshots; repeated identical source records are idempotent."""
        inserted = 0
        with self._db() as db:
            for event in events:
                payload = event.as_dict()
                encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
                # Retrieval time is local bookkeeping, not source content. Ignore
                # it for idempotency while retaining it in the first stored receipt.
                hash_payload = {key: value for key, value in payload.items() if key != "received_at"}
                hash_encoded = json.dumps(hash_payload, sort_keys=True, separators=(",", ":"), default=str)
                digest = hashlib.sha256(hash_encoded.encode("utf-8")).hexdigest()
                cursor = db.execute(
                    "INSERT OR IGNORE INTO event_versions "
                    "(source, source_id, payload_hash, event_time, received_at, ticker, event_json) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (event.source, event.source_id, digest, event.event_time.isoformat(),
                     event.received_at.isoformat(), event.ticker.upper(), encoded),
                )
                inserted += cursor.rowcount == 1
        return inserted

    def load_events(self, thesis_id: str | None = None) -> list[Event]:
        """Load local snapshots in append order; event-time order is applied by replay."""
        del thesis_id  # Events are source snapshots; thesis filtering happens in the evaluator.
        with self._db() as db:
            rows = db.execute("SELECT event_json FROM event_versions ORDER BY event_version_id").fetchall()
        events: list[Event] = []
        for row in rows:
            item = json.loads(row["event_json"])
            events.append(Event(
                source=item["source"], source_id=item["source_id"], ticker=item["ticker"],
                event_time=datetime.fromisoformat(item["event_time"]),
                received_at=datetime.fromisoformat(item["received_at"]), kind=item["kind"],
                fields=item.get("fields", {}), complete=bool(item.get("complete", True)),
                mode=item.get("mode", "replay"),
            ))
        return events

    def record_evaluation(self, evaluation: Evaluation, previous_status: str | None = None) -> bool:
        """Append an evaluation once; returns whether it created a new row."""
        receipt = {
            "thesis_id": evaluation.thesis_id,
            "thesis_version": evaluation.thesis_version,
            "status": evaluation.status,
            "evaluated_at": evaluation.evaluated_at.isoformat(),
            "event_ids": evaluation.event_ids,
            "predicates": [item.__dict__ for item in evaluation.predicates],
            "reasons": evaluation.reasons,
            "input_hash": evaluation.input_hash,
            "output_hash": evaluation.output_hash,
            "mode": evaluation.mode,
        }
        with self._db() as db:
            cursor = db.execute(
                "INSERT OR IGNORE INTO evaluations VALUES (?, ?, ?, ?, ?, ?, ?)",
                (evaluation.output_hash, evaluation.thesis_id, evaluation.thesis_version,
                 evaluation.evaluated_at.isoformat(), evaluation.status, evaluation.input_hash,
                 json.dumps(receipt, sort_keys=True, default=str)),
            )
            created = cursor.rowcount == 1
            if created and previous_status != evaluation.status:
                db.execute(
                    "INSERT OR IGNORE INTO transitions "
                    "(thesis_id, thesis_version, previous_status, next_status, evaluation_hash, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (evaluation.thesis_id, evaluation.thesis_version, previous_status,
                     evaluation.status, evaluation.output_hash, evaluation.evaluated_at.isoformat()),
                )
            return created

    def latest_status(self, thesis_id: str) -> str | None:
        with self._db() as db:
            row = db.execute(
                "SELECT status FROM evaluations WHERE thesis_id = ? ORDER BY evaluated_at DESC LIMIT 1",
                (thesis_id,),
            ).fetchone()
            return row["status"] if row else None

    def transitions(self, thesis_id: str) -> list[dict[str, str | None]]:
        with self._db() as db:
            rows = db.execute(
                "SELECT previous_status, next_status, evaluation_hash, created_at FROM transitions "
                "WHERE thesis_id = ? ORDER BY transition_id",
                (thesis_id,),
            ).fetchall()
            return [dict(row) for row in rows]

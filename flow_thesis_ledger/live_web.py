"""Responsive live UW + OpenAI workflow, bound to localhost only."""

from __future__ import annotations

import argparse
import json
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from typing import Any, Callable
from urllib.parse import urlsplit

from .ai import ThesisCompileError, ThesisCompiler
from .models import Thesis
from .store import LedgerStore
from .uw_api import UWAPIError, UWClient
from .uw_ingest import FlowAlertPoller, classify_uw_error, normalize_flow_alerts


MAX_BODY = 12_000
PAGE_LIMIT = 50


def _thesis_json(thesis: Thesis | None) -> dict[str, Any] | None:
    if thesis is None:
        return None
    return {
        "id": thesis.id, "version": thesis.version, "ticker": thesis.ticker,
        "statement": thesis.statement, "status": thesis.status,
        "freshness_seconds": thesis.freshness_seconds,
        "required_fields": list(thesis.required_fields),
        "conditions": [asdict(condition) for condition in thesis.conditions],
    }


def _status_payload(store: LedgerStore, thesis: Thesis | None, summary: str | None,
                    verified: dict[str, bool] | None = None) -> dict[str, Any]:
    verified = verified or {}
    credentials = {
        "uw": {"present": bool(os.environ.get("UW_API_KEY")), "verified": verified.get("uw", False)},
        "openai": {"present": bool(os.environ.get("OPENAI_API_KEY")), "verified": verified.get("openai", False)},
    }
    if thesis is None:
        return {"thesis": None, "message": "No thesis yet.", "credentials": credentials}
    events = [event for event in store.load_events() if event.ticker == thesis.ticker]
    notes = store.load_thesis_notes(thesis.id, thesis.version)
    return {
        "thesis": _thesis_json(thesis), "summary": summary or notes["summary"],
        "uncertainties": notes["uncertainties"], "evidence_refs": notes["evidence_refs"],
        "evaluation": store.latest_receipt(thesis.id),
        "credentials": credentials,
        "evidence": [{
            "source_id": event.source_id, "event_time": event.event_time.isoformat(),
            "field_names": sorted(event.fields), "fields": event.fields,
            "complete": event.complete, "mode": event.mode,
        } for event in events[-20:]],
        "transitions": store.transitions(thesis.id),
    }


def _error_payload(error: Exception) -> tuple[int, dict[str, Any]]:
    if isinstance(error, UWAPIError):
        return (error.status or 502), {
            "error": "UW request failed safely", "status": error.status,
            "category": classify_uw_error(error),
        }
    if isinstance(error, ThesisCompileError):
        return 502, {"error": "AI thesis compilation failed", "status": error.status,
                     "category": error.category or "compiler_error"}
    if isinstance(error, PermissionError):
        return 403, {"error": str(error)}
    if isinstance(error, ValueError):
        return 400, {"error": str(error)}
    if isinstance(error, OSError):
        return 503, {"error": "Local persistence failed", "category": type(error).__name__}
    return 500, {"error": "Operation failed safely", "category": type(error).__name__}


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    content_type = handler.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
    if content_type != "application/json":
        raise ValueError("Content-Type must be application/json")
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        raise ValueError("Invalid request length") from None
    if not 0 < length <= MAX_BODY:
        raise ValueError("Request body must be between 1 byte and 12 KB")
    try:
        value = json.loads(handler.rfile.read(length).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("Request body must be valid JSON") from None
    if not isinstance(value, dict):
        raise ValueError("Request body must be a JSON object")
    return value


def serve(host: str = "127.0.0.1", port: int = 8766, db_path: Path = Path(".local/flow-thesis-ledger.sqlite3")) -> None:
    if host not in {"127.0.0.1", "localhost"}:
        raise ValueError("Live console must bind to localhost to protect API credentials and personal data")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    store = LedgerStore(db_path)
    restored_thesis = store.load_thesis()
    restored_notes = store.load_thesis_notes(restored_thesis.id, restored_thesis.version) if restored_thesis else {}
    state: dict[str, Any] = {
        "thesis": restored_thesis, "summary": restored_notes.get("summary", ""),
        "verified": {},
    }
    state_lock = Lock()
    jobs: dict[str, dict[str, Any]] = {}
    jobs_lock = Lock()
    executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="flow-thesis-job")
    page = Path(__file__).with_name("live_console.html").read_bytes()
    asset_dir = Path(__file__).with_name("assets")
    asset_types = {
        "ledger-mark.svg": "image/svg+xml",
        "flow-path.svg": "image/svg+xml",
        "empty-ledger.svg": "image/svg+xml",
    }
    from .web import _page_data
    replay_snapshot = Path(__file__).parents[1] / "examples" / "thesis_replay.json"
    replay_data = _page_data(replay_snapshot)
    replay_json = json.dumps(replay_data, separators=(",", ":"), default=str).replace("</", "<\\/")
    replay_page = Path(__file__).with_name("viewer.html").read_text(encoding="utf-8").replace("__REPLAY_DATA__", replay_json).encode("utf-8")

    def perform_prepare(payload: dict[str, Any], progress: Callable[[str], None]) -> dict[str, Any]:
        ticker, statement = payload.get("ticker"), payload.get("statement")
        if not isinstance(ticker, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9.]{0,9}", ticker.strip()):
            raise ValueError("Ticker must be 1 to 10 letters/numbers")
        if not isinstance(statement, str) or not statement.strip() or len(statement) > 3000:
            raise ValueError("Thesis statement must contain 1 to 3000 characters")
        ticker = ticker.strip().upper()
        progress("Fetching live Unusual Whales Flow Alerts…")
        response = UWClient().flow_alerts({
            "ticker_symbol": ticker, "limit": PAGE_LIMIT, "all_opening": "false",
        })
        state["verified"]["uw"] = True
        progress("Normalizing and persisting the live alert page…")
        events = normalize_flow_alerts(response.body)
        matches = [event for event in events if event.ticker == ticker]
        if not matches:
            raise ValueError("UW returned no normalizable Flow Alerts for this ticker; choose a ticker with current alerts")
        store.append_events(matches)
        progress(f"Compiling a structured thesis from {len(matches)} normalized UW alert(s)…")
        thesis_id = "thesis-" + uuid.uuid4().hex[:16]
        proposal = ThesisCompiler().compile(
            statement, thesis_id=thesis_id, expected_ticker=ticker, events=matches,
        )
        state["verified"]["openai"] = True
        store.save_thesis(proposal.thesis, datetime.now(timezone.utc).isoformat())
        store.save_thesis_notes(
            proposal.thesis.id, proposal.thesis.version, proposal.summary,
            proposal.uncertainties, proposal.evidence_refs,
        )
        from .engine import evaluate_snapshot
        initial_evaluation = evaluate_snapshot(proposal.thesis, store.load_events())
        store.record_evaluation(initial_evaluation, None)
        with state_lock:
            state["thesis"], state["summary"] = proposal.thesis, proposal.summary
            result = _status_payload(store, state["thesis"], state["summary"], state["verified"])
        result["message"] = f"Draft compiled from {len(matches)} normalized UW alert(s), then deterministically evaluated. Review before approval."
        result["initial_evaluation"] = initial_evaluation.status
        result["possibly_truncated"] = len(response.body.get("data", [])) >= PAGE_LIMIT
        return result

    def perform_approve(progress: Callable[[str], None]) -> dict[str, Any]:
        progress("Persisting your approval for read-only monitoring…")
        with state_lock:
            thesis = state["thesis"]
            if thesis is None or thesis.status != "draft":
                raise PermissionError("A current draft must be reviewed before approval")
            activated = store.activate_thesis(
                thesis, human_approved=True, approved_at=datetime.now(timezone.utc).isoformat(),
            )
            state["thesis"] = activated
            result = _status_payload(store, activated, state["summary"], state["verified"])
        result["message"] = "Read-only monitoring approved. No trading action is available."
        return result

    def perform_poll(progress: Callable[[str], None]) -> dict[str, Any]:
        with state_lock:
            thesis = state["thesis"]
            if thesis is None or thesis.status != "monitoring" or not store.is_activated(thesis.id, thesis.version):
                raise PermissionError("Review and approve a draft before monitoring")
        progress("Fetching live Flow Alerts from UW…")
        result = FlowAlertPoller(UWClient(), store, limit=PAGE_LIMIT).poll_once(thesis)
        state["verified"]["uw"] = True
        progress("Evaluating new evidence and recording the state transition…")
        with state_lock:
            payload = _status_payload(store, thesis, state["summary"], state["verified"])
        payload["message"] = "Live Flow Alerts polled and deterministic state evaluated."
        payload["poll"] = {
            "http_status": result["http_status"], "received": result["received"],
            "normalized": result["normalized"], "inserted": result["inserted"],
            "possibly_truncated": result["possibly_truncated"],
            "evaluation_recorded": result["evaluation_recorded"],
        }
        return payload

    def start_job(kind: str, operation: Callable[[Callable[[str], None]], dict[str, Any]]) -> tuple[int, dict[str, Any]]:
        with jobs_lock:
            for existing in jobs.values():
                if existing["status"] in {"queued", "running"}:
                    return 409, {"error": "Another operation is still running", "job_id": existing["id"]}
            job_id = uuid.uuid4().hex
            job = {"id": job_id, "kind": kind, "status": "queued", "progress": "Queued…"}
            jobs[job_id] = job

        def run() -> None:
            def progress(message: str) -> None:
                with jobs_lock:
                    job["status"], job["progress"] = "running", message
            try:
                result = operation(progress)
                with jobs_lock:
                    job["status"], job["progress"], job["result"] = "complete", "Complete", result
            except Exception as error:
                status, safe_error = _error_payload(error)
                with jobs_lock:
                    job["status"], job["progress"] = "failed", "Failed safely"
                    job["http_status"], job["error"] = status, safe_error

        executor.submit(run)
        return 202, {"job_id": job_id, "status": "queued", "progress": "Queued…"}

    class Handler(BaseHTTPRequestHandler):
        server_version = "FlowThesisLedger/1.0"

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; connect-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; base-uri 'none'; frame-ancestors 'self'")
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, status: int, body: dict[str, Any]) -> None:
            self._send(status, json.dumps(body, separators=(",", ":"), default=str).encode(), "application/json; charset=utf-8")

        def _check_local_request(self) -> bool:
            host_header = self.headers.get("Host", "")
            if host_header not in {f"127.0.0.1:{port}", f"localhost:{port}"}:
                self._send_json(403, {"error": "Invalid local host"})
                return False
            origin = self.headers.get("Origin")
            if origin and urlsplit(origin).netloc != host_header:
                self._send_json(403, {"error": "Cross-origin requests are not allowed"})
                return False
            return True

        def do_GET(self) -> None:  # noqa: N802
            if not self._check_local_request():
                return
            route = urlsplit(self.path).path
            if route in {"/", "/index.html", "/overview", "/new-thesis", "/evidence", "/replay", "/settings"}:
                self._send(200, page, "text/html; charset=utf-8")
            elif route == "/synthetic-replay":
                self._send(200, replay_page, "text/html; charset=utf-8")
            elif route.startswith("/assets/"):
                name = route.rsplit("/", 1)[-1]
                if name not in asset_types:
                    self._send_json(404, {"error": "Not found"})
                    return
                self._send(200, (asset_dir / name).read_bytes(), asset_types[name])
            elif route == "/api/status":
                with state_lock:
                    self._send_json(200, _status_payload(store, state["thesis"], state["summary"], state["verified"]))
            elif route.startswith("/api/jobs/"):
                job_id = route.rsplit("/", 1)[-1]
                with jobs_lock:
                    job = jobs.get(job_id)
                    if job is None:
                        self._send_json(404, {"error": "Job not found"})
                    else:
                        self._send_json(job.get("http_status", 200), {key: value for key, value in job.items() if key != "http_status"})
            else:
                self._send_json(404, {"error": "Not found"})

        def do_POST(self) -> None:  # noqa: N802
            if not self._check_local_request():
                return
            route = urlsplit(self.path).path
            try:
                payload = _read_json(self)
                if route == "/api/prepare":
                    status, result = start_job("prepare", lambda progress: perform_prepare(payload, progress))
                elif route == "/api/approve":
                    if payload.get("approve") is not True:
                        raise PermissionError("Explicit approval is required")
                    status, result = start_job("approve", perform_approve)
                elif route == "/api/poll":
                    status, result = start_job("poll", perform_poll)
                else:
                    self._send_json(404, {"error": "Not found"})
                    return
                self._send_json(status, result)
            except Exception as error:
                status, safe_error = _error_payload(error)
                self._send_json(status, safe_error)

        def log_message(self, format: str, *args: Any) -> None:
            return

    httpd = ThreadingHTTPServer((host, port), Handler)
    httpd.daemon_threads = True
    print(f"Flow Thesis Ledger live console: http://{host}:{port} (localhost only)")
    print("Credentials are read from process environment and never sent to the browser or logs.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        executor.shutdown(wait=True, cancel_futures=True)
        store.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local live UW thesis console")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--db", type=Path, default=Path(".local/flow-thesis-ledger.sqlite3"))
    args = parser.parse_args()
    try:
        serve(args.host, args.port, args.db)
    except OSError as error:
        raise SystemExit(f"Could not start local console ({type(error).__name__})") from None


if __name__ == "__main__":
    main()

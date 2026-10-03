"""Local, read-only replay viewer for a labeled snapshot."""

from __future__ import annotations

import json
import sys
from datetime import timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .__main__ import load_snapshot
from .engine import replay


def _page_data(snapshot: Path) -> dict[str, Any]:
    thesis, events, label = load_snapshot(snapshot)
    evaluations = replay(thesis, events)
    return {
        "label": label,
        "thesis": {
            "ticker": thesis.ticker,
            "statement": thesis.statement,
            "version": thesis.version,
        },
        "timeline": [
            {
                "evaluated_at": item.evaluated_at.astimezone(timezone.utc).isoformat(),
                "status": item.status,
                "event_ids": item.event_ids,
                "reasons": item.reasons,
                "predicates": [predicate.__dict__ for predicate in item.predicates],
                "input_hash": item.input_hash,
                "output_hash": item.output_hash,
            }
            for item in evaluations
        ],
    }


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m flow_thesis_ledger.web <snapshot.json> [port]")
    snapshot = Path(sys.argv[1]).resolve()
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
    data = json.dumps(_page_data(snapshot), separators=(",", ":"), default=str)
    page_path = Path(__file__).with_name("viewer.html")
    template = page_path.read_text(encoding="utf-8")
    page = template.replace("__REPLAY_DATA__", data.replace("</", "<\\/"))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib handler method name
            if urlsplit(self.path).path not in {"/", "/index.html"}:
                self.send_error(404)
                return
            body = page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            # No market payloads or request headers are written to logs.
            return

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Local replay viewer: http://127.0.0.1:{port} (fixture: {data and snapshot.name})")
    print("Data mode is declared by the snapshot. This server is bound to localhost only.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

"""Compile a user statement into a draft JSON thesis; no draft is auto-activated."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .ai import ThesisCompileError, ThesisCompiler


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile a market thesis into a structured draft")
    parser.add_argument("--statement", required=True, help="User-authored thesis statement")
    parser.add_argument("--output", type=Path, help="Optional local draft JSON path")
    args = parser.parse_args()
    try:
        proposal = ThesisCompiler().compile(args.statement)
    except ThesisCompileError as error:
        print(json.dumps({"status": "not_compiled", "http_status": error.status,
                          "error_category": error.category or "compiler_error"}), file=sys.stderr)
        raise SystemExit(1) from None
    data = {
        "thesis": {
            "id": proposal.thesis.id, "version": proposal.thesis.version,
            "ticker": proposal.thesis.ticker, "statement": proposal.thesis.statement,
            "conditions": [asdict(item) for item in proposal.thesis.conditions],
            "required_fields": proposal.thesis.required_fields,
            "freshness_seconds": proposal.thesis.freshness_seconds,
            "status": "draft",
        },
        "compiler_summary": proposal.summary,
        "uncertainties": proposal.uncertainties,
        "requires_user_review_before_monitoring": True,
    }
    serialized = json.dumps(data, indent=2, sort_keys=True, default=str)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
        print(f"Draft proposal written to {args.output}; it is not active until reviewed.")
    else:
        print(serialized)


if __name__ == "__main__":
    main()

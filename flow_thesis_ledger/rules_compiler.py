"""No-cost, deterministic thesis draft builder for explicitly entered rules."""

from __future__ import annotations

import math
from collections.abc import Iterable

from .ai import ThesisProposal
from .models import Condition, Event, Thesis


def compile_rule_based(
    statement: str,
    *,
    thesis_id: str,
    expected_ticker: str,
    total_premium_threshold: float,
    events: Iterable[Event],
) -> ThesisProposal:
    """Build a reviewable draft without making an AI request or inferring rules."""
    if not statement.strip() or len(statement) > 3000:
        raise ValueError("statement must contain 1 to 3000 characters")
    if not math.isfinite(total_premium_threshold) or not 0 <= total_premium_threshold <= 1e15:
        raise ValueError("total-premium threshold must be between 0 and 1e15")
    ticker = expected_ticker.strip().upper()
    if not ticker:
        raise ValueError("ticker is required")
    matching = [event for event in events if event.ticker.upper() == ticker]
    if not matching:
        raise ValueError("a rule-based draft requires at least one matching UW event")

    threshold = float(total_premium_threshold)
    conditions = (
        Condition(
            id="c1", field="total_premium", comparator="gte", threshold=threshold,
            kind="support", description=f"A fresh Flow Alert has total premium at or above ${threshold:,.2f}.",
        ),
        Condition(
            id="c2", field="total_premium", comparator="lt", threshold=threshold,
            kind="weaken", description=f"A fresh Flow Alert has total premium below ${threshold:,.2f}.",
        ),
    )
    thesis = Thesis(
        id=thesis_id, version=1, ticker=ticker, statement=statement.strip(),
        conditions=conditions, required_fields=("total_premium",),
        freshness_seconds=86400, status="draft",
    )
    event_refs = tuple(dict.fromkeys(event.source_id for event in matching))
    return ThesisProposal(
        thesis=thesis,
        summary=(
            "Rule-based draft created locally from your explicit total-premium threshold; "
            "no OpenAI request was made. The deterministic evaluator will use fresh UW alert evidence."
        ),
        uncertainties=(
            "Total premium is an observed aggregate; it does not establish trade direction or predict price movement.",
            "The state remains indeterminate when matching evidence is stale, incomplete, or missing total premium.",
            "This no-cost mode uses the numeric threshold you entered and does not infer rules from free text.",
        ),
        evidence_refs=event_refs,
    )

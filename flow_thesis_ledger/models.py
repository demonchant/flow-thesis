"""Small typed domain model. API payloads are normalized before entering this layer."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Literal

Comparator = Literal["gte", "gt", "lte", "lt", "eq"]
ConditionKind = Literal["support", "weaken", "invalidate"]
EventKind = Literal["flow_alert", "constituent_trade", "context"]
ThesisStatus = Literal[
    "draft", "monitoring", "supported", "weakened", "invalidated", "indeterminate", "closed"
]


@dataclass(frozen=True)
class Condition:
    """A supported, deterministic predicate over normalized event fields."""

    id: str
    field: str
    comparator: Comparator
    threshold: float | str | bool
    kind: ConditionKind
    description: str

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.field.strip():
            raise ValueError("condition id and field are required")
        if self.comparator not in {"gte", "gt", "lte", "lt", "eq"}:
            raise ValueError(f"unsupported comparator: {self.comparator}")
        if self.kind not in {"support", "weaken", "invalidate"}:
            raise ValueError(f"unsupported condition kind: {self.kind}")


@dataclass(frozen=True)
class Thesis:
    id: str
    version: int
    ticker: str
    statement: str
    conditions: tuple[Condition, ...]
    required_fields: tuple[str, ...] = ()
    freshness_seconds: int = 900
    status: ThesisStatus = "monitoring"

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.ticker.strip() or not self.statement.strip():
            raise ValueError("thesis id, ticker, and statement are required")
        if self.version < 1:
            raise ValueError("thesis version must be positive")
        if self.freshness_seconds <= 0:
            raise ValueError("freshness_seconds must be positive")
        ids = [condition.id for condition in self.conditions]
        if len(ids) != len(set(ids)):
            raise ValueError("condition ids must be unique")


@dataclass(frozen=True)
class Event:
    """Normalized source observation; `received_at` is distinct from event time."""

    source: str
    source_id: str
    ticker: str
    event_time: datetime
    received_at: datetime
    kind: EventKind
    fields: dict[str, Any] = field(default_factory=dict)
    complete: bool = True
    mode: Literal["live", "replay"] = "replay"

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.ticker.strip():
            raise ValueError("event source_id and ticker are required")
        if self.event_time.tzinfo is None or self.received_at.tzinfo is None:
            raise ValueError("event timestamps must include a timezone")

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["event_time"] = self.event_time.isoformat()
        result["received_at"] = self.received_at.isoformat()
        return result


@dataclass(frozen=True)
class PredicateResult:
    condition_id: str
    kind: ConditionKind
    matched: bool | None
    observed: Any
    threshold: float | str | bool
    event_ids: tuple[str, ...]
    reason: str | None = None


@dataclass(frozen=True)
class Evaluation:
    thesis_id: str
    thesis_version: int
    status: ThesisStatus
    evaluated_at: datetime
    event_ids: tuple[str, ...]
    predicates: tuple[PredicateResult, ...]
    reasons: tuple[str, ...]
    input_hash: str
    output_hash: str
    mode: Literal["live", "replay"]

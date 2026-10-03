# Flow Thesis Ledger: Architecture

## Design constraints

- Read-only financial research tool; no trading, portfolio execution, or advice.
- UW observations are primary inputs. Retain only what is permitted; never make an API key visible in browser code or public repository.
- AI can propose structured interpretation and explain evidence, but deterministic code validates evidence and sets thesis state.
- Replay must preserve “what was known when.” Later corrections create a new version; they must not rewrite historical demo evidence silently.
- Basic/trial capability is not live-smoke-tested. Use REST flow polling for MVP. UW's flow-alert WebSocket docs say personal access requires Advanced; treat streaming as out of scope unless the account tier is confirmed.
- Local-first demo by default because individual API terms limit redistribution, including derived data.

## System flow

```text
User thesis / known UW alert ID
        ↓
AI clarification (schema-constrained proposal, evidence requirements, uncertainty)
        ↓
User confirms the proposed test definition
        ↓
UW REST retrieval (flow alerts → flow alert by ID → relevant legs/contract or price context)
        ↓
Typed normalization (source ID, event time, received time, ticker, contract, observed fields)
        ↓
Deduplication + event-time ordering + completeness/freshness checks
        ↓
Deterministic predicate evaluator + baseline/outcome evaluator
        ↓
Versioned thesis state + append-only observation/transition ledger
        ↓
Scheduled poll or optional UW WebSocket event (entitlement-dependent)
        ↓
Compare new event against cursor, thesis version and prior evidence
        ↓
Re-evaluate → status transition or indeterminate reason
        ↓
AI explanation grounded only in cited evidence IDs (schema + citation validation)
        ↓
Replay verification + evidence artifact + user result
```

## Components (keep modular, not distributed)

1. **Web UI:** create/edit thesis, confirm AI schema, view current state, evidence, history and replay outcome. No direct UW key in browser.
2. **Local API/service:** owns credential and UW requests; returns minimized typed records. In development, runs as one process.
3. **UW adapter:** explicit endpoint methods, pagination/cursors, response validation, request budget/freshness metadata. Exact paths/fields to be confirmed against downloaded official OpenAPI and trial key.
4. **Normalizer:** maps source-specific fields into a small canonical event model; preserve original source record ID and timestamps.
5. **Thesis compiler:** AI structured output only. Proposed schema contains ticker(s), time bounds, conditions from an allow-list, thresholds, invalidation clauses, required fields, evidence references and uncertainty. User approves before monitoring.
6. **Evaluator:** pure deterministic functions; outputs predicate status, evidence IDs, missing-data codes and state transition proposal. No free-form AI claims.
7. **Ledger/store:** SQLite for local MVP; tables for thesis versions, source events (minimal permitted data), source references, cursor/checkpoints, evaluations, transitions, replay runs and evidence manifest. Append transitions; edits create a new thesis version.
8. **Scheduler/stream adapter:** polling at a conservative interval by default. Optional WebSocket consumer if trial scope permits; persist cursor/checkpoint, idempotency key, heartbeat and last event time. No queue/microservice required for a single entrant demo.
9. **Evidence exporter:** deterministic JSON manifest and human-readable result. Default export omits UW payload values and keys; include source IDs/timestamps only if terms allow.

## Canonical data shape

```json
{
  "source": "unusual_whales",
  "source_endpoint": "configured endpoint identifier",
  "source_id": "opaque UW record id",
  "ticker": "symbol",
  "event_time": "provider timestamp",
  "received_at": "UTC timestamp",
  "event_kind": "flow_alert | constituent_trade | contract_snapshot | price_context",
  "contract_key": "normalized OCC-like key or null",
  "fields": {},
  "completeness": "complete | partial | unknown",
  "raw_payload_hash": "sha256, if storage terms permit"
}
```

The shape is an internal target, not an assertion that the UW API returns these exact fields. Build an adapter only after obtaining official OpenAPI and exercising the key.

## State machine

```text
draft → monitoring → supported
                   ↘ weakened → monitoring (new evidence)
                   ↘ invalidated
                   ↘ indeterminate → monitoring (fresh complete data)
                   ↘ closed
```

- `supported` means the encoded criteria currently pass; it does not mean the market thesis is true or profitable.
- `weakened` means a configured adverse condition crossed its threshold while core evidence remains incomplete or mixed.
- `invalidated` means an explicit user-approved falsification condition is met.
- `indeterminate` means required input is missing/stale/contradictory or the evidence type is not represented. Fail closed; do not retain green state on stale data.
- A newly amended data record creates a superseding evaluation and transition; historical snapshots remain immutable.

## Point-in-time and replay design

Every evaluation records: thesis version, rule version, source event IDs, event time and retrieval time, data watermark/cursor, market calendar session, freshness decision, missing records, evaluator version and output hash. Replay reads an immutable snapshot in event-time order and executes the same pure evaluator used live. Enforce event time `<= evaluation_time` for each outcome feature to prevent look-ahead. Distinguish reprocessing the same snapshot from incorporating later corrections.

## AI contract

**Input:** user's natural-language claim, supported conditions/metrics, allowed horizons, fetched evidence metadata and explicitly cited source IDs.  
**Output:** validated JSON fields: `clarifying_questions[]`, `proposed_conditions[]`, `required_fields[]`, `invalidates_if[]`, `uncertainties[]`, `evidence_refs[]`, `explanation`.  
**Decision:** propose a test definition and explain the already computed result. It does not decide the result, choose a ticker, construct a trade, call arbitrary tools, or execute side effects.  
**Validation:** strict schema, allowed condition enum, numeric bounds, evidence-reference membership, and user confirmation. If invalid, reject and ask for edit; do not autocorrect hidden thresholds.  
**Recovery:** deterministic status remains available if model is down; explanation can show a template. Persist prompt/model/version metadata without leaking keys or disallowed market data.

## UW endpoint plan (provisional)

Endpoint names/categories confirmed from UW official docs catalog; request/response contracts and trial entitlements remain to be verified through OpenAPI/key smoke test.

| Need | Official documented endpoint category | Use |
|---|---|---|
| Candidate event stream | Flow Alerts | Query bounded ticker/time/filter set; primary market event input |
| Underlying alert facts | Flow Alert by ID | Retrieve trades constituting an alert and multi-leg-related trades |
| Multi-leg corroboration | Multi-Leg Option Trades / Legs | Exclude or represent strategy legs correctly |
| Context / historical checks | Option contract historic/intraday/volume profile; stock state/stock candles; ticker flow/Greeks only if needed | Measure selected user predicates and replay outcome |
| Realtime (optional) | Flow-alert WebSocket channel `flow-alerts` | Personal access requires Advanced according to UW docs; exclude from Basic/trial MVP. REST polling reports its actual freshness instead. |

Do not ingest all-market full tape or subscribe to broad feeds for MVP. Do not assume WebSocket is in trial scope from the pricing display.

## Reliability, safety and permissions

- API adapter uses timeouts, retry only on transient/429 errors with bounded exponential backoff, respects reset headers/rate ceilings, and retries idempotent reads only.
- Cursor/checkpoint update happens only after event persistence; duplicate source IDs are idempotent.
- A circuit breaker marks feed `unavailable`; no fabricated event or stale “supported” status.
- Data quality is first-class: event-time lag, source age, missing fields, pagination completeness and market-session status appear beside every result.
- Local key in environment/OS secret store; no frontend exposure, logs, screenshots, fixture files, Git history or support bundle.
- Avoid persistent raw UW payload unless API terms permit. Prefer references/hashes/minimized fields and confirm retention rights.
- Public demo: use a UW-approved exception or synthetic/redacted proof; label synthetic data. Do not publish derived market results until license terms are clear.

## Components deliberately excluded

No multi-agent architecture (one bounded extraction task), vector database/RAG (structured time-series evidence), microservices (single-user workload), Kafka/queue (not needed until scale or strict delivery semantics), blockchain (no consensus need), autonomous trading (unsafe and outside user outcome), and general-purpose backtest engine (only a narrow cohort replay is justified).

## Strongest alternative architectures considered

### Backup A: Catalyst-to-tape event study

```text
Earnings / SEC / news event from UW
  → validate issuer + provider/event timestamps
  → normalize event and market-session window
  → retrieve UW flow/price/IV observations inside a fixed, point-in-time window
  → AI classifies catalyst into a constrained taxonomy with source references
  → deterministic event cohort + matched baseline + coverage/confounder checks
  → persist event version, source IDs, inclusion/exclusion decisions and metrics
  → late filing/headline correction → rejoin/recompute a new cohort version
  → replay check + confidence/uncertainty summary
  → user sees what happened in the cohort, not a causal claim
```

This is the strongest backup if Flow Thesis Ledger cannot obtain enough Flow Alerts access/history. Its difficult work is issuer/time matching and confounder-resistant event cohorts. It is less compelling as the lead because UW already offers event/news/earnings analysis surfaces, event timestamps may be corrected, and event studies demonstrate correlation rather than a visible user-owned state workflow.

### Backup B: Earnings implied-move calibration

```text
Upcoming earnings event
  → freeze pre-announcement UW option/IV snapshot and timestamp
  → deterministic implied-move estimate + contract liquidity/coverage checks
  → persist forecast distribution inputs and earnings-event version
  → actual report/first regular-session price data arrives
  → compute realized move from predeclared timestamp/horizon
  → join historical UW earnings/options cohorts using point-in-time rules
  → compare calibration by IV/liquidity/regime bucket and baseline
  → replay held-out cohort with leakage checks
  → user sees calibration error and sample/uncertainty, not a forecast or trade
```

This has strong measurement and demo potential if historical options snapshots are available. It is less adaptive, depends on reliable point-in-time pre-earnings option data and can be mistaken for a forecast/profit product. It should be chosen only if access validation favors it or user discovery favors earnings research over thesis tracking.

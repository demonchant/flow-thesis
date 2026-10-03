# Flow Thesis Ledger: Risk and Failure Model

## Highest-impact risks

| Risk | Likelihood / impact | Detection | Behavior/recovery | Product/pitch impact |
|---|---|---|---|---|
| Trial key lacks endpoint or WebSocket entitlement | Medium / High; exact account unknown | Startup capability smoke test; endpoint error classification | Disable unavailable source and report unsupported mode; use an explicitly labeled fixture for offline replay | Narrow “continuous” claims to supported polling/history |
| API access or rate limits interrupt monitoring | Medium / High | HTTP status, usage/reset headers, freshness lag | Bounded backoff, persist cursor before acknowledgement, dedupe on resume, mark state stale/indeterminate | Do not call process continuous while feed is unavailable |
| UW terms prohibit public demo display/derived results on individual key | High / High pending written guidance | Read terms, get UW/event organizer answer | Local-key execution; mask public artifacts or use synthetic data; seek required commercial license/permission | Public live-data screenshots/videos/hosting blocked until clarified |
| Flow signal is interpreted as intent/direction with certainty | High / High | Separate observed fields from inferences; audit language | No user trade recommendation; represent unknown intent as unknown | Avoid “whale knows” / “smart money” claims |
| AI invents conditions, data, or explanations | Medium / High | Strict schema, allowed metric enum, evidence-ref membership, deterministic result | Reject invalid schema; leave state from deterministic evaluator; fallback templated explanation | AI is assistant, not source of truth |
| Missing/late/contradictory events yield stale green state | Medium / High | Freshness thresholds, cursor gaps, partial field checks, timestamp reconciliation | Set `indeterminate` or `unavailable`; recover by paging/replay; append correction version | No continuous monitoring claim without proven coverage |
| Duplicate alerts create duplicate evidence/count inflation | Medium / Medium | Unique source ID + event-window fingerprint; duplicate metric | Idempotent insert and evaluation; replay from persisted cursor | Show duplicates suppressed, not “exactly-once” without proof |
| Multi-leg alert mistaken for a directional position | Medium / High | Query alert constituents/leg links and UW multi-leg feed | Mark strategy/partial grouping, avoid single-leg bullish/bearish claim | A core uncertainty in the demo; not infer intent |
| Open-interest/tape snapshots are not aligned | Medium / High | Capture event vs receive time, field provenance, available-at timestamp | Avoid definitive open/close classifications; widen uncertainty or exclude | No claim that volume > OI definitively reveals position intent |
| Backtest leakage / selection bias | Medium / High | Immutable event time, versioned rules, predefined cohort, chronological split | Exclude events with unavailable point-in-time data; publish sample limitations | No “predictive edge” or profitability claims |
| Wrong ticker/contract or corporate-action mismatch | Low-Medium / High | Contract key validation, ticker map, expiry/split checks | Quarantine malformed records; replay after correction | Do not show invalid observations as thesis evidence |
| AI/provider outage | Medium / Low-Medium | Timeout and provider status | Monitoring and deterministic evaluator continue; explanation template; schema proposal requires user edit | No dependence of state machine on model uptime |
| Local store corruption/process crash | Low-Medium / High | DB integrity/startup checkpoint validation | Transactional append, backup export, resume from cursor; mark gap if source retention exceeded | Narrow persistence guarantees to verified behavior |
| Terms/API spec drift | Medium / Medium | Contract validation and startup response checks | Adapter version, feature disablement, clear actionable error | Re-verify before demo; docs are dynamic |
| No public competitors indexed | High / Medium | Inspect event Discord manually | Treat competitive landscape as unknown and invite user-supplied links | Do not claim uniqueness or first |
| Hackathon due date not shown | Medium / High | Confirm Discord thread/event contact | Prioritize hard promise and proof; adjust scope when cutoff confirmed | Time feasibility remains an estimate |

## Data trust model

**Confirmed observations:** source endpoint and record ID, provider timestamps, returned fields, retrieval time, API status, completeness/freshness checks.  
**Deterministic inference:** the system's named rule evaluated those observations at a defined time.  
**AI interpretation:** explanation/structuring language that cites permitted records and can be rejected.  
**Unknown:** open/close intent not present/derivable with certainty, market causality, missing/late data, unavailable history, unverified trial capabilities.

UI and evidence artifacts should label these classes explicitly. Avoid conflating options buyer-side, option position opening, or expected underlying direction.

## Failure state behavior

- Required source unavailable: keep last known snapshot but show age; transition current evaluation to `indeterminate` after freshness cutoff.
- Partial alert detail: never treat absent legs/fields as evidence that no legs/conditions exist; show `partial` and list missing evidence.
- Conflicting observations: show both source IDs/times, apply predeclared tie/ordering policy or return `indeterminate`.
- Invalid AI output: reject and preserve rule/state; ask for clarification.
- Duplicate/out-of-order event: idempotently ignore duplicate; buffer/order by provider event time within bounded lag; record late arrival and append revised evaluation.
- Corrected historical data: never overwrite former evidence artifact; create a new snapshot/version and compare results.
- API 401/403: stop repeated attempts and report key/plan entitlement issue; do not leak key in logs.
- API 429/5xx/network: bounded retry with jitter/reset header, persist cursor, then mark feed unavailable. Do not spin.
- Process restart: load thesis/rule versions, last committed cursor and last health state; replay unprocessed records if still available or report a gap.

## Recovery claims allowed only after proof

Do not claim exactly-once processing; implement idempotent effects and demonstrate duplicate suppression. Do not claim real-time unless measured end-to-end latency is reported and entitlements confirmed. Do not claim data integrity because a request returned 200; reconcile record count/cursor or explicitly state verification limits. Do not claim continuous monitoring if the app runs only while the user's process is alive without an external scheduler.

## Financial safety / product language

The application analyzes observable market records against user-authored criteria. It does not say what to buy, sell, hold or trade; it does not identify a trader's intent or predict price movement. Display source timestamps, uncertainty, missing data and the exact rule. Use an explicit not-financial-advice disclaimer, but do not use the disclaimer to excuse unsupported assertions.

# Selected Concept: Flow Thesis Ledger

## One-sentence product

Flow Thesis Ledger turns a user's market thesis into a versioned, evidence-backed test, tracks the UW observations that support or contradict it, and shows when the thesis changes state—without recommending or placing trades.

## User and problem

**Primary user:** an options-flow researcher or retail market participant who saves a hypothesis after seeing an unusual-flow event and wants to know what subsequent evidence actually did to that hypothesis.

**Pain:** an alert arrives as a momentary signal. Users often remember supporting evidence and forget contradictory evidence, confuse a trade at/near ask with a new long position, or cannot reproduce why they believed a hypothesis later. UW itself explains that buy/sell side is inferred from NBBO proximity, mid fills are approximated, and not every buy opens or every sell closes a position. [UW Options Flow guide](https://docs.unusualwhales.com/features/2-options-flow/)

**Outcome:** every saved thesis has a precise test definition, data freshness status, source-linked evidence, explainable state transitions, and—where data access permits—a historical replay result and comparison baseline. It is a research record, not a trade signal.

## Why the concept passes the gate

- **UW is indispensable:** UW option-flow alert detail and related market/contract data are the evidence stream being audited. With another generic finance API, the core flow observations and UW source references disappear.
- **Technical depth is problem-driven:** ambiguous claims must be converted into valid predicates; observations must be point-in-time joined, deduplicated and versioned; the state machine must distinguish false, missing and stale evidence; replay must avoid look-ahead leakage.
- **AI performs bounded cognitive work:** clarify an ambiguous statement, propose an explicit schema, explain a completed transition from cited facts. It cannot choose an unsupported result or label a trade as definitely opening/closing.
- **Deterministic analysis constrains AI:** schema validation, allowed endpoints, evidence references, metric calculations, state transitions and outcome evaluation are ordinary code.
- **Operational behavior is visible:** a saved thesis changes from `monitoring` to `weakened`, `invalidated` or `indeterminate` after a new event or data gap; the system records why.
- **Proof can be reproduced:** same input policy + same immutable event snapshot + same code/rule version must yield the same status and metrics.
- **Time fit:** one month is adequate for a single-thesis workflow with direct API ingestion, local persistence, a replay tool and a concise UI; no microservices or multi-agent architecture required.

### Idea gate scores (1–5)

| Criterion | Score | Reason |
|---|---:|---|
| Problem strength | 3 | Plausible recurring research discipline problem; no user interviews yet |
| User value | 3 | Clear audit/recall benefit, but adoption and willingness to use remain unvalidated |
| Technical depth | 4 | Point-in-time evidence, dedup, versioning, event state, replay and failure semantics are specified |
| AI necessity | 3 | Unstructured claim clarification benefits from AI; deterministic limited vocab remains fallback |
| Agentic potential | 2 | Bounded retrieval and result inspection are useful; autonomous agent loop is not justified |
| Statefulness | 4 | Thesis and evidence evolve over time |
| Integration depth | 4 | UW data directly drives rule evaluation and state transitions |
| Sponsor indispensability | 4 | UW is the primary flow source; exact trial access is not yet tested |
| Technical novelty | 3 | Distinctive planned combination; uniqueness not proven |
| Demoability | 4 | Can show claim → evidence → status transition → replay, with access/terms condition |
| Proof potential | 4 | Rule version, timestamps, source references, snapshot and deterministic output are designed |
| Failure/recovery potential | 4 | Duplicates, stale feed, missing fields, invalid AI output have defined behaviors |
| Repository quality potential | 3 | Artifacts are planned; implementation/reproducibility do not yet exist |
| Submission clarity | 3 | Short story; financial data terms and contest requirements need confirmation |
| Time feasibility | 3 | One-month event window, exact cutoff and API scope unknown |
| Competitive differentiation | 3 | Better than standard API+LLM in design; competitor forum not inspected |

**Threshold:** use the existing V2 worksheet: at least **40/64** and no mandatory floor below 2 for problem, user value, depth, sponsor indispensability, proof, demo or time. These evidence-anchored scores total **54/64**; all mandatory floors pass. This is a discovery go, not a claim that implementation is already proven. The concept carries two shipping gates: exact API entitlement smoke test and permissible public demo/data display. The comparative table in `UW_CANDIDATE_IDEAS.md` uses a separate 1–5 scale and should not be conflated with this gate.

## Hardest promise (mandatory)

> “When a later UW observation or a data-freshness change affects a saved thesis, Flow Thesis Ledger records the resulting state and the conditions behind it; the same snapshot and rule version reproduce the same result.”

This promise must be implemented end to end. The currently available code only evaluates supplied normalized snapshots; it does not yet poll UW. The planned Basic/trial path is REST polling, so the UI and pitch must state its actual interval and freshness. Never promise continuous or sub-second surveillance based on scheduled polling. Source corrections are only handled if the chosen endpoint exposes them and that behavior is separately verified.

## Judge memory sentence

“They will remember this project because it showed a saved flow thesis change state when contradictory evidence arrived, then replayed the exact evidence that caused the change.”

## One-minute proof path

1. Start with a real historical or current UW flow event (mark historical/live accurately).
2. Enter the user's statement; show AI's proposed typed predicates and the user's confirmation.
3. Retrieve source records and run deterministic checks for side, multi-leg, volume/OI and price/flow conditions.
4. Show initial thesis status plus evidence/counter-evidence and timestamps.
5. Introduce the next real event or a clearly labeled replay event from a stored UW snapshot.
6. Re-evaluate; show the exact changed predicate and state transition.
7. Run replay and show identical output hash/rule version.
8. Explain the user result: “your stated condition no longer holds” or “insufficient fresh data,” never a buy/sell instruction.

## Scope boundaries

### MVP

- One user-owned thesis at a time (one user profile can store several, but concurrency is not a demo requirement).
- Constrained schema covering ticker, event/observation window, measurable conditions, invalidation condition, horizon and evidence requirements.
- Read-only UW API ingestion. No broker connection, order placement or portfolio access.
- State labels: `draft`, `monitoring`, `supported`, `weakened`, `invalidated`, `indeterminate`, `closed`.
- Source lineage, freshness and rule version on every observation/transition.
- Historical replay only for data actually available from permitted endpoints; clearly mark fixtures and trial restrictions.
- AI structured proposal + source-grounded explanation. Deterministic evaluation owns the result.

### Explicit non-goals

No market predictions, financial advice, trade recommendations, autonomous execution, social sharing of UW data, generic ticker chatbot, general dashboard, arbitrary user code, or “smart money” intent claims. No claim of statistical edge unless a suitably sized out-of-sample evaluation supports it.

## Kill / pivot conditions

1. If the trial cannot retrieve detailed flow and any required point-in-time history, pivot to a replay-only research tool using documented accessible data or choose the earnings calibration candidate after endpoint smoke check.
2. If terms prohibit the required public visual proof and UW does not approve an exception, keep the app local-key only and use a public demo with redacted/synthetic data; if the contest rejects that proof, ask the organizer for compliant format before public deployment.
3. If early users cannot provide a falsifiable thesis that the schema can represent, narrow the supported thesis types and disclose them; do not pretend to parse any market thesis.
4. If competitor research reveals UW already ships user-authored thesis lifecycle plus evidence replay, pivot to a differentiated cohort evaluation or reject.
5. If one-minute demo requires fabricated data or an unsupported inference, the concept fails the claim-to-proof gate.

## Readiness decision

**Idea gate: PASS, implementation may start with local/offline core and API contract validation.** **Public live-data demo: CONDITIONAL / NOT CLEARED** until UW data-use terms are clarified. The top priority after initial build is an endpoint smoke check with an actual trial key and an end-to-end replay whose market observations are transparently labeled.

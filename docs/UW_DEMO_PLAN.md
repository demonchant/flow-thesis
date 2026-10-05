# Flow Thesis Ledger: One-Minute Demo Plan

## Goal

Show that this is a stateful research workflow, not a flow dashboard, chat response or trading bot. Prove the hardest promise: new or revised evidence changes a saved thesis state, records the reason, and deterministic replay reproduces it.

## Data mode rules

The Replay page uses actual UW observations saved in the local ledger. It has no bundled example or fallback. Record the real live workflow only where the UW terms permit the intended display; never alter a live value or describe historical replay as a newly arriving event. Keep credentials, account identifiers, and raw API payloads off screen.

## 60-second path

| Time | Screen/action | Judge should learn |
|---|---|---|
| 0–5s | Thesis page: one-sentence user claim and “research, not advice” label | Real user need: remember and test a hypothesis, not chase an alert |
| 5–12s | Enter a claim; AI returns a structured test proposal with thresholds, required evidence and uncertainty questions | AI performs constrained extraction, not market prediction |
| 12–20s | Confirm schema; fetch one UW flow alert and its constituent/related data | UW source is in the critical path; show actual endpoint/source timestamp where display rights permit |
| 20–30s | Evidence card distinguishes observed facts from inference; deterministic predicates set initial state | AI does not control the evaluation; unknowns remain unknown |
| 30–40s | A second event or recorded replay event arrives; show a predicate failing or freshness gap | System observes a changed condition and transitions state rather than preserving stale certainty |
| 40–49s | Open transition trace: prior/new values, rule version, event IDs, reason | State change is explainable and auditable |
| 49–56s | Re-run identical replay; output hash/status matches | Behavior is reproducible |
| 56–60s | Show final user result and limitation | “This specified condition is invalidated/indeterminate”; no buy/sell recommendation |

## Demonstration data plan

1. Before implementation freeze, run the exact endpoint entitlement smoke check and record account tier/key type without storing the secret.
2. Select one historical event with an available constituent endpoint and two subsequent observations in an allowed window. Choose based on data completeness, not on a winning result.
3. Preserve the timeline, query filters, API response times, data freshness, rule version, and replay outcome. Do not choose only flattering examples; report the predeclared case-selection rule.
4. Include one adverse case (incomplete feed, duplicate, stale timestamp, or conflicting evidence) that deterministically results in `indeterminate` or a recovery transition.
5. Keep a second offline fixture for repeatability and mark every displayed row as fixture/replay.
6. Publicly share the live-data recording only within the data display rights that apply to this account. Do not replace restricted live values with fabricated market evidence.

## On-screen visual hierarchy

1. Thesis statement and version.
2. State + as-of/freshness badge.
3. Conditions table: criterion, current measurement, required threshold, support/counter status, source reference.
4. Transition timeline with a named cause.
5. Replay/evaluation panel: sample count, benchmark, excluded records and limitations.
6. AI explanation pane clearly labeled as explanation; keep “observed / inferred / unknown” separated.

Avoid a chart-first opening, decorative agent avatars, green/red trade signal colors, or an AI answer that asserts directional conviction. The main moment is thesis status changing and the evidence trace explaining why.

## Failure rehearsal

- Duplicate the same event ID: one evaluation only; duplicate count recorded.
- Remove a required field: status becomes indeterminate with missing field listed.
- Make data older than freshness limit: show stale state; last known value is visibly stale.
- Return malformed AI schema: proposal rejected, deterministic status unchanged.
- Simulate 429/API timeout in local replay: checkpoint remains, bounded retry then feed unavailable.
- Introduce a corrected record: preserve prior evaluation, append a superseding one, explain version difference.

## Judge memory and 30-second explanation

“Flow Thesis Ledger turns a saved options-flow thesis into a test. It tracks evidence for and against the user's own conditions, changes state when new observations arrive, and can replay the evidence behind every change. It analyzes market data; it does not tell you what to trade.”

## Proof caveat

The demo is not evidence of profitable signals or predictive performance. A single case demonstrates the workflow only. Any historical cohort claim needs predeclared windows, enough cases, baseline, exclusions and out-of-sample evaluation, all described in `UW_EVIDENCE_PLAN.md`.

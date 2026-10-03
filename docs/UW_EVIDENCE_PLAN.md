# Flow Thesis Ledger: Evidence and Measurement Plan

## Claim ledger

| Claim | Evidence required | Pass criterion | Do not claim |
|---|---|---|---|
| UW flow data drives the test | Sanitized endpoint identifier, actual success status, source event ID/timestamp, normalized-record link | A real entitled request is used in live mode; replay fixture is separately labeled | “Live UW integration” if only fixture data is loaded |
| Thesis is converted into a bounded test | AI output JSON, schema version, validation result, user confirmation | Invalid/unsupported condition is rejected; accepted thresholds are visible | “Understands any thesis” |
| Evidence changes thesis state | Before/after state, rule/evaluator versions, event IDs, predicate deltas | New event or stale/missing-data condition produces expected transition | “Continuously monitors” if manual or scheduled refresh is used |
| AI explanation is grounded | Evidence refs in output and citation validator result | Every factual statement references an evaluator fact/source in supplied evidence | “AI verifies market truth” |
| Replay is reproducible | Snapshot manifest, input count, sorted event hashes, code/rule version, output hash | Re-run same snapshot yields identical deterministic status/metrics | “Independent verification” if replay uses same unvalidated source only |
| Historical analysis is meaningful | Point-in-time cohort specification, exclusions, metrics, baseline, interval, test split | Report full cohort and uncertainty; avoid tuning on holdout | “Predicts returns” or “edge” from a small demo |
| Failure recovery works | Fault injection logs plus final checkpoint/state | Duplicate safe, gap visible, bounded retry/checkpoint replay succeeds | “Fault tolerant” based only on exception handling |

## Live access verification record

On 2026-10-03, the user ran `python -m flow_thesis_ledger.verify_uw` from the PowerShell session containing `UW_API_KEY`. The Flow Alerts list endpoint returned HTTP 200 with a `data` array (one row); the detail endpoint returned HTTP 200 with an alert/trades object. This is evidence of authenticated access to those two routes at that time only. It does not validate field-level normalization, endpoint history, quota, other trial entitlements, or the poller's end-to-end live behavior. No key, payload, ticker, or alert ID was recorded here.

On 2026-10-03, a generic structured thesis compiler smoke call reached the OpenAI Responses API and returned HTTP 429. No proposal was produced. The user reports the key is valid but the account has no API credit. Successful live AI compilation remains unverified; the deterministic schema-validation and sanitized AI-failure paths are unit-tested. This is not an official hackathon blocker: UW's event page recommends MCP + an AI agent but says builders can build however they want. Do not claim successful AI generation until credits are available and the call succeeds.

## Evidence artifact format

Machine-readable `evidence-manifest.json` (or a local non-exported equivalent until license rights are confirmed):

```json
{
  "manifest_version": 1,
  "mode": "live | replay | synthetic",
  "as_of_utc": "timestamp",
  "source": "unusual_whales",
  "endpoint_ids": [],
  "source_ids": [],
  "thesis_id": "opaque id",
  "thesis_version": 1,
  "rule_version": "semver-or-hash",
  "evaluator_version": "semver-or-hash",
  "input_snapshot_hash": "sha256",
  "event_count": 0,
  "excluded_event_count": 0,
  "freshness": "fresh | stale | partial | unknown",
  "state_before": "monitoring",
  "state_after": "indeterminate",
  "transition_reasons": [],
  "deterministic_output_hash": "sha256",
  "ai_explanation_validated": false,
  "limitations": []
}
```

Do not put raw UW payload or secret API key in a public artifact. Confirm whether source IDs or derived metrics themselves can be shared under the applicable license before export.

## Evaluation plan

### 1. Core evaluator correctness

Use small, hand-checkable snapshots for each supported predicate. Verify boundary conditions, missing values, timestamp order, duplicate source IDs, out-of-order arrival, and revised records. Expected state transitions are authored before test execution. Tests are required before claiming the evaluator is reliable; do not inflate test count.

### 2. AI schema quality

Create a small labeled set of user claims (at least 20 varied statements if time allows): supported, ambiguous, impossible/unavailable field, contradictory condition, non-falsifiable, out-of-bounds numeric threshold, and explicit uncertainty. Measure:

- exact schema validity;
- unsupported-field rejection;
- clarifying question precision for ambiguous statements;
- preservation of user thresholds;
- fabricated condition count (target zero in test set);
- evidence reference validity (target 100% of emitted refs exist).

Use deterministic mocks for the model call in logic tests; separately record model/provider and actual structured-output checks for the demonstration. If the set is smaller, report its size and do not generalize.

### 3. Replay/backtest

- Predeclare condition definition, signal time, observation horizon, primary underlying outcome metric and comparator before reviewing results.
- Enforce point-in-time cutoff and use data available at that event time only.
- Deduplicate correlated alerts so one burst does not masquerade as many independent observations.
- Include all eligible events after fixed rules, not only favorable cases.
- Compare to a simple baseline (same ticker/time window or matched non-alert sessions if feasible); report sample count, exclusions, median and distribution/interval, not only mean or total return.
- Include lookback/window choices and API coverage. A 2-year advertised account history is an entitlement ceiling, not confirmation that each target endpoint has 2 years of usable data.
- Use chronological holdout/walk-forward split. Keep tuned cases out of the final evaluation.
- Do not claim causal impact, profit, predictive accuracy, or an investable edge from observational market data.

### 4. Operational evidence

Record API latency/status, rate-limit headers if present, retries, cursor advances, duplicates ignored, event lag, missing required fields, stale intervals and recovery duration. Never store or print authorization values. The demo can show counts and status without exposing restricted data.

## Minimum evidence gate before external claims

1. One end-to-end live UW data path or clearly labeled replay, using exact entitled endpoint.
2. One positive and one adverse/indeterminate thesis case.
3. Identical replay output for same snapshot and evaluator version.
4. Duplicate, stale and malformed-AI cases observed and correctly handled.
5. README links each major claim to a source code path, machine evidence and demo moment.
6. Public data sharing rights have been resolved or public artifacts use safe redaction/synthetic data.

# My technicality gap

## Finding

RecallReady is not a toy CRUD app. In the supplied archive it has a typed 8-table Convex model, scoped reads/writes, signed AgentMail webhooks, idempotent inbound events, realtime state, deterministic exact-model matching, source-run records, and unit/backend tests. Calling it “technically shallow” would be inaccurate.

The gap is that the product promise and the automated system do not yet meet: the product says it keeps watching; `convex/crons.ts` is empty and labels household fan-out future work. It has a valuable critical-path workflow, but less algorithmic novelty, failure/recovery coverage, and independently reproducible evidence than Parallel. Parallel's solver is not a collection of sponsor calls: it formally optimizes the product's central constraint and then shows repair. PlusOne offers another useful reference for measured source quality and durable workflow boundaries, though its test coverage appears weak in this ZIP.

PlusOne ownership is unconfirmed. The comparison below is based on RecallReady as the confirmed personal project. If PlusOne is also yours, its lack of an automated test script/files is an additional recurring gap, while its Firecrawl evaluation and workflow implementation are capabilities worth retaining.

## Critical

### 1. Turn one-shot source lookup into truthful persistent monitoring

- **Why:** the useful promise is future warning without the user remembering to search. The source archive contains no cron schedule.
- **Problem solved:** notices published after a product was added currently have no confirmed automated path to reach the household.
- **When:** whenever the product claims it monitors/watches/keeps current, and new data can appear independently.
- **Implementation:** durable source cursor/check records; scheduled source refresh; normalize and deduplicate notices by authority ID/content hash; ingest globally once; match against indexed product signatures in bounded batches; persist per-source freshness/status; retry transient errors with caps; show last successful scan and degraded source state. Avoid per-household crawling if a source can be ingested once and matched centrally.
- **Demonstrate:** add a fixture notice after the product exists; show the next scheduled run detect it, record provenance, create a match, and update a second client live. Show an API failure as “source stale/check failed,” not “no recalls.”
- **Test:** duplicate source page/event; harmless page change; changed model list; rate limit; partial batch crash/retry; old notice; exact model mismatch; concurrent scan; stale freshness; ensure no false “clear.”
- **Failure:** a crawler silently misses notices, source schema changes, or a retry repeats alerts. Treat source health separately from match state; dedupe alerts with stable keys; never clear open safety states based on missing data.
- **Judging story:** directly fulfills the differentiating promise; proves Convex scheduling/state and Firecrawl ingestion create a sustained capability.

### 2. Build a measured matcher/evidence evaluation

- **Why:** an exact matcher test on three examples does not establish real-world precision/recall or safe handling of incomplete model identifiers.
- **Problem solved:** false negatives and false positives in safety alerts.
- **When:** decisions with asymmetric harm, weak/noisy upstream data, and user action.
- **Implementation:** versioned, consent-safe fixture corpus from official notice/product pairs; labeled exact, near, partial, absent, and conflicting identifiers; deterministic matching first; optional AI extraction may propose fields but cannot bypass verified source/model rules; use uncertainty states for human review. Record matcher version, normalized values, rule reasons, and source record IDs.
- **Demonstrate:** a true match, a same-brand wrong-model non-match, and an ambiguous notice routed to review. Show the source and exact field comparison.
- **Test:** precision/recall on fixed fixtures; malformed/empty extraction; punctuation/region suffix normalization; model-family false positive; duplicate recall; source authority/provenance missing.
- **Failure:** overfitting to small fixtures or treating model confidence as correctness. Keep a held-out fixture set and expose uncertainty.
- **Judging story:** replaces “AI found a recall” with a checkable safety decision.

### 3. Close the submission evidence loop

- **Why:** RecallReady `docs/SUBMISSION.md` and `hackathon.md` leave social posting/submission as pending, though the deadline is now past. This is an operational evidence gap, not an architecture defect.
- **Problem solved:** judges cannot score a project they cannot find, open, or verify.
- **When:** every submission, with a hard pre-deadline checklist and evidence capture.
- **Implementation:** one final commit/release containing exact live URL, video URL/duration, public repo, start date, tested build commands, sponsor actions actually demonstrated, and submission confirmation reference. Remove stale “ready/pending” statements only when replaced by factual completed status.
- **Demonstrate:** reviewer clicks README → live app → demo → source/evidence in under a minute.
- **Test:** cold-open links without login, clean setup/build, compare submitted commit to demo commit, verify build log and URL.
- **Failure:** expired link, private demo, wrong production backend, unsubmitted form. Keep a saved submission receipt and immutable release tag.
- **Judging story:** reduces reviewer uncertainty and prevents preventable eligibility/presentation losses.

## High value

### 4. Use durable bounded workflow state instead of ad hoc action chains

- **Why:** source retrieval and matching may span retries/time windows; status must survive reloads and restarts.
- **Implementation:** explicit scan lifecycle (`queued → fetching → normalizing → matching → complete|partial|failed`), durable run IDs, step outputs, idempotency keys, bounded retries/backoff and retryable failure classification.
- **Use when:** operation has multiple independent external calls, long execution, or recovery needs. Avoid adding a workflow component to a short transactional operation.
- **Demo/test/failure:** interrupt after ingestion and before matching; resume without duplicate notices/alerts; verify partial source health remains visible.
- **Judging story:** provides the recovery moment that a judge can watch and a repository can prove.

### 5. Make AI output typed, validated, and reviewable

- **Why:** current extraction is useful, but required-field presence alone does not validate plausibility or ambiguity.
- **Implementation:** strict schema; normalize type/length/unit; check extraction against email evidence where possible; classify uncertain fields; quarantine invalid candidates; persist model/schema version and outcome. Deterministic matcher owns actionability.
- **Use when:** model handles messy human text, not exact decisions already expressible as code.
- **Demonstrate/test:** malformed JSON, omitted model, unrelated product, conflicting model mentions; show manual correction and reprocessing.
- **Judging story:** AI contributes cognition while safety boundaries remain explicit.

### 6. Show state transitions and audit evidence in the product

- **Why:** RecallReady already has `events` and `sourceRuns`, but demo/reviewer should distinguish last success, in-progress, partial failure, alert delivered, and user resolution.
- **Implementation:** linked run ID → source record → matched product/recall → notification delivery record → user resolution, with timestamps and status transitions.
- **Use when:** a user's result must be explained or revisited.
- **Test:** each event points to real records; no “sent” unless provider result exists; repeat action is idempotent.
- **Judging story:** every technical claim can be followed from action to consequence.

## Optional (only if problem warrants)

- **Optimization/constraint solver:** useful only if RecallReady expands into actual household remedy planning (multiple products, deadlines, travel/repair options); unnecessary for simple recall matching.
- **Multi-agent design:** no current need. A single extraction action plus deterministic matcher is safer and sufficient.
- **Vector search/RAG:** not a substitute for exact model safety matching. Consider only for searching long documents after canonical records and citations exist.
- **Presence/live collaboration:** realtime household state is already useful; elaborate cursor/gesture features are unrelated to safety and low priority.
- **Queues/sharding:** introduce only after ingestion volume or execution limits demonstrate need.

## Specific comparative lesson

Parallel turns dynamic conference assignment into a measurable optimization objective and uses that exact system to repair after a constraint change. RecallReady should not copy its optimizer. It should create an equally problem-native mechanism: recurring source ingestion, versioned deterministic match evaluation, and a recovery path where source failure cannot masquerade as a clean result. That is the highest-value route from “good architecture” to “deep technical proof.”

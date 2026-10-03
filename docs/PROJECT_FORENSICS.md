# Project forensics

## Scope and confidence

Reviewed the three supplied ZIP archives without unpacking them, plus the public GitHub README/build log for `thomasnguyen/ourspaces-app` and the official Convex All Gas event page. Reading compressed entries allowed inspection of manifests, schemas, workflow code, selected tests, demo scripts, and submission artifacts while avoiding another full checkout on a volume that reported no free space.

**Provenance limits:** RecallReady is identified by the user as their submission. Parallel is a comparison project from the provided archive. PlusOne is in the same folder, but its ownership is not established here; this report treats it as a project in the dataset, not definitely as the user's work. The user identifies OurSpaces as the winner. The public event page gives criteria and says winners were to be announced September 25, but I did not find an official results page confirming the award. Winner status is therefore **user-reported**, not independently verified. The YouTube links and the RecallReady MP4 were not visually/audio reviewed in this environment; demo observations below use scripts and repository claims and mark the rest unknown.

Evidence labels: **CONFIRMED** means visible in source or an official event artifact; **INFERRED** is a conclusion from implementation structure; **UNKNOWN** means the archive cannot establish it. Claims in project READMEs/logs about production behavior are identified as documented claims, not independent live verification.

## Shared judging context

The official event asked for an everyday app, creativity/usefulness, substantive Convex use, real work from OpenAI, Firecrawl and AgentMail, a public live URL, social sharing, and a real-product video under three minutes. Required artifacts included a public repo, a `hackathon.md` log, deployment and demo. Deadline: September 22, 2026, 12:00 PM PT. [Official event and judging criteria](https://luma.com/convex-allgas-hackathon).

This is a qualitative mapping to explicit criteria, not a score reconstruction: no judging sheets or official relative weights were supplied.

## RecallReady — user-owned submission

### Product and chain

- **Problem/user:** households miss product recalls because they forget exact model identifiers and do not regularly search official sources. The user is a household member or caregiver.
- **One sentence:** Forward a receipt; RecallReady adds the purchased item to a household inventory, checks safety notices, and guides a household through an evidence-backed remedy.
- **Primary action/outcome:** forward purchase email; the item appears in shared inventory, and a relevant notice can become a tracked safety issue.
- **Non-trivial constraint:** false positives are harmful; a brand-level resemblance is insufficient for an actionable alert. Source authority, exact product/model evidence, household routing, and replay safety matter.

```text
Forwarded email
→ signed AgentMail webhook
→ sender + inbox routed to household
→ OpenAI extracts product identity (strict JSON schema)
→ Convex records inbound event/product and emits live state
→ Firecrawl fetches CPSC recall material on a user-triggered check
→ deterministic identifier/brand matcher creates an explainable match
→ AgentMail can send an alert; member acknowledges/resolves it
→ activity and household UI show the result
```

**Chain depth:** roughly 8 meaningful stages. **Level 3** for the core end-to-end workflow (multi-step API orchestration with durable records); some Level 4 qualities in persistent household state, idempotent webhook ingestion, and explicit resolution. It does not qualify as an autonomous monitoring/recovery system in the supplied source.

### Architecture evidence

- **CONFIRMED in ZIP:** React/Vite/TypeScript frontend; Convex database, queries, mutations, actions, HTTP actions, realtime subscriptions and static hosting; 8 schema tables (`households`, `members`, `products`, `recalls`, `matches`, `events`, `sourceRuns`, `inboundEmails`); household-scoped indexes and product full-text index.
- **CONFIRMED in ZIP:** OpenAI Responses API with strict receipt extraction schema; Firecrawl retrieval; AgentMail webhook and outbound messages; Svix-style signature/time-window verification; webhook event deduplication; explicit demo/fresh household modes; source-run status/provenance; exact normalized model matching utility.
- **CONFIRMED in ZIP:** browser-session token plus server-side household access checks; no third-party account auth. Outbound keys stay server-side according to architecture documentation.
- **CONFIRMED in ZIP:** two automated test files (`convex/app.test.ts`, `src/lib/safety.test.ts`) with backend bootstrap/access/inventory/workflow cases and matcher cases. README claims additional verification commands and deployment checks; tests were not run here.
- **UNKNOWN:** live production credentials/state, whether the final Vibe Apps submission was completed, independently verified delivery, source coverage/refresh cadence, and monitoring behavior after this archive was made.

### Hidden complexity and AI

The user sees “forward receipt and get warned.” Hidden work is sender-to-household routing, parsing messy receipts, canonical product identifiers, matching against noisy official notices, source attribution, replay protection, keeping issue status consistent, and preserving household privacy. AI is an **AI feature** for extracting fields from unstructured mail. Its structured output affects inventory state, but deterministic code is appropriately responsible for matching and safety status. The source has a minimal output presence check; broader semantic validation/uncertainty routing is not established. No multi-tool agent, replanning loop, or AI evaluation suite is present in the supplied files.

### Critical gap found in source

`convex/crons.ts` is empty and says production household fan-out can be enabled after connecting live source credentials. Thus the source supports on-demand scans, but the persistent “keeps watching” promise is not implemented as recurring monitoring in this archive. `sourceRuns` and scheduled-function language do not prove a schedule. This is the highest-impact gap because ongoing monitoring is the product's defining value after onboarding. A failed scan must also never be interpreted as a clean bill of health.

### Submission/proof status

The README and `docs/SUBMISSION.md` provide setup, architecture, demo, live URL, public repo and safety boundary. `docs/SUBMISSION.md` explicitly has social posting and judging submission unchecked; `hackathon.md` also says social post pending and submission ready. Those are direct repository artifacts, and the date deadline has passed. They do not prove whether submission happened later via the form. User-reported social numbers in the conversation are not corroborated by supplied screenshots or platform access and remain **UNKNOWN** here.

## Parallel — comparison project

### Product and chain

- **Problem/user:** an organization sends teammates to a conference and wants broad coverage of weighted goals without duplicate attendance, while still respecting preferences, availability, time conflicts, and schedule changes.
- **One sentence:** Parallel converts a conference agenda and team goals into an optimized coverage plan, then repairs it when a teammate's availability changes and compiles source-backed takeaways.
- **Primary action/outcome:** import agenda, add people/goals, publish plan; the useful result is distributed session coverage, repaired assignments, collected notes and a delivered brief.
- **Non-trivial constraints:** overlapping talks, attendance capacity, pins/preferences, availability, change minimization, noisy agenda extraction, emailed natural-language replies, and source-grounded final claims.

```text
Agenda URL + team goals/members
→ Firecrawl fetch with content hash/source record
→ OpenAI structured extraction and time normalization
→ Convex stores sessions and goal/session scores
→ deterministic constrained optimizer computes assignments + objective/proof
→ plan revision is published
→ AgentMail sends assignment/reply requests
→ signed webhook + OpenAI parses intent and quotes
→ constraints/revision update; stale plans are rejected/repaired
→ candidate cover is proposed and teammate accepts by email
→ accepted coverage and source-linked takeaways persist
→ brief generator validates citations against stored notes and delivers by email
```

**Chain depth:** 10+ meaningful stages. **Level 5** for the demonstrated workflow: multi-system state, explicit revisions, deterministic optimization, event ingestion, repair, evidence, and delivery. This depth directly serves schedule coordination rather than existing just as infrastructure.

### Architecture evidence

- **CONFIRMED in ZIP:** React/Vite; Convex with 19 tables described in build log/schema, indexed state, 6 mounted components (static hosting, workflow, workpool, Firecrawl, rate limiter, action retrier), durable agenda import, scoring fan-out, cron/scheduler, signed Svix webhook, event and send records.
- **CONFIRMED in ZIP:** structured OpenAI schemas for agenda extraction, goal relevance, replies, and briefs; deterministic interval/conflict/coverage/assignment engine. `optimizePlanWithProof` has a bounded exact search path and fallback search (exact node cap is 120,000); solver records status, objective, upper bound, and nodes explored. Repair objective penalizes changed assignments.
- **CONFIRMED in ZIP:** 57 `.test.ts` test files (409 tests are a build-log/README claim, not recounted by execution here), including brute-force comparisons, property/determinism/constraint/repair tests and adversarial email, replay, stale-write, privacy, solver-hostility, and agenda-noise tests. Tests were not executed.
- **CONFIRMED in docs/code:** demo and verified-run materials state conference scenario was played out and explicitly disclose that nobody attended, some teammates were placeholders, and some run replies/takeaways were written for the run. This is valuable provenance honesty; it means the workflow's external interface is real, while human experiential claims are simulated.
- **UNKNOWN:** independent verification of public deployment, email deliveries and metrics; whether all claimed production data records remain reachable; official placement.

### AI role / depth

AI is a combination of **extractor, ranker, reply classifier, and constrained report writer**. It normalizes input and supplies semantic scores/intents. The solver—not the model—enforces overlap and coverage rules. Email intent only changes workflow state when confidence and application guards allow it; brief sources are checked against stored notes. This is an **AI workflow with bounded agentic edges**, not an unrestricted autonomous planner. Evidence for tool calling/replanning: application-controlled calls to Firecrawl/OpenAI/AgentMail and deterministic re-optimization after revision changes; no LLM tool loop is required for the core solver.

## PlusOne — project in dataset; ownership unconfirmed

### Product and chain

- **Problem/user:** engaged couple planning multi-day events need vendor discovery, inquiry, quote comparison, follow-up, guest coordination, and budget visibility without email/spreadsheet fragmentation.
- **One sentence:** PlusOne researches vendors for each wedding need, drafts and sends approved inquiries through a wedding-specific inbox, turns replies into comparable quotes, and keeps the shared budget live.
- **Constraint:** vendor facts and prices must come from actual read pages/messages; emails must not be sent without approval; cultural/multi-event needs and budget state must remain coherent.

```text
Wedding brief + vendor need
→ Convex workflow asks OpenAI to plan search queries
→ Firecrawl searches and maps/scrapes candidate vendor/contact/pricing pages
→ OpenAI extracts structured cards; deterministic plausibility/source checks
→ candidates persist and stream to couple
→ OpenAI drafts personalized vendor emails
→ human edits/approves before send
→ AgentMail sends; signed webhook receives replies
→ OpenAI classifies/extracts quote and flags; deterministic checks update quote/budget
→ cron follows up with a bounded count, then escalates to a person
→ shared Convex plan updates live
```

**Chain depth:** 9 stages. **Level 4**: durable multi-step workflows and email events, bounded autonomous follow-up, with human approval for first outreach and booking. The workflow is useful for ongoing wedding coordination.

### Architecture evidence

- **CONFIRMED in ZIP:** Vite/React, Convex Auth, Convex database and realtime queries, 18-table schema described in build log, workflow + workpool + static hosting, scheduled hourly follow-up, signed AgentMail webhook, Firecrawl search/map/scrape, OpenAI via AI SDK structured generation, file storage for attachments.
- **CONFIRMED:** research workflow stages and bounded parallel batches, retries, max candidate/time limits; outbound email drafts need user confirmation; webhook first-touch is idempotent on message/event id; unknown senders do not automatically trigger replies (product docs); roles are viewer/planner/owner.
- **CONFIRMED:** scripts and JSON record measurable Firecrawl evaluations. The source doc reports vendor-source hits, email/price/rating coverage, iteration from one-page scraping to mapped contact/pricing pages, and manual verification of review values. These are author-produced experiments; methodology/raw data exist, but results have not been independently reproduced here.
- **UNKNOWN:** production vendor emails' external recipients and booking outcomes; automated test suite (no test/spec files or test script appeared in the archive manifest); live deployment status today.

### AI depth

AI performs query planning, vendor card extraction/ranking, email drafting, inbound reply classification/quote extraction, RSVP parsing, and a wedding-context assistant. Assistant tools can initiate research/add vendor needs; outreach has a confirmation gate. This is an **AI workflow plus limited tool-using assistant**, with deterministic budget, authorization, source, and confirmation boundaries. The exact breadth of evaluation beyond Firecrawl/review quality scripts is not established.

## OurSpaces — user-identified winner; public repo inspected, source checkout unavailable

### Product and chain

- **Problem/user:** friends and groups lose decisions, photos, assignments and context in fast-moving group chats.
- **One sentence:** OurSpaces gives a group a persistent shared live canvas and inbox where emails, links, plans and collaborative activities become visible objects.
- **Primary outcome:** a shared space persists group context and synchronizes changes while people are present.
- **Non-trivial constraint:** simultaneous edits/presence, anonymous onboarding, email routing, diverse widget state, and asynchronous external data must stay coherent and understandable.

```text
Group creates/joins a space
→ Convex identity/member/space state
→ users edit widgets, vote, paint, message; presence/gesture rules coordinate live changes
→ email enters per-space AgentMail webhook or a URL is pasted/emailed
→ router deduplicates/routes email; OpenAI classifies/fills a widget OR Firecrawl extracts page
→ Convex writes typed widget/event state
→ realtime subscriptions update every open participant
→ recap/ask-space workflow retrieves persisted messages/widgets, generates a grounded response
→ changes are visible in board/activity and can be queried after reload
```

**Chain depth:** 8+ stages. **Level 4/5** depending on pathway: realtime collaborative state plus several asynchronous integrations and durable workflows; strongest paths include deduplication and persisted grounding, but source-level recovery/verification could not be checked locally.

### Architecture evidence and limits

- **CONFIRMED from public README, not local source:** React/Vite/TypeScript + Convex; 13 tables/30 indexes/FTS/vector index in the current README; 17 component usages claimed; functions listed as 45 queries, 72 mutations, 34 actions plus HTTP actions; storage, crons, workflow, workpool, rate limiting, retry/cache, persistent streaming, agent/RAG, presence, aggregation, batch worker. README says Convex Auth silent guest identity and optional email-code join.
- **CONFIRMED from public README:** AgentMail routes inbound emails to a space and sends replies; Firecrawl enriches URLs, searches and crawls; OpenAI files mail/generates questions and “ask the space” output; Convex is the source of truth and realtime UI layer.
- **UNKNOWN:** those counts and behaviors independently confirmed against source at this revision; specific test coverage; demo edit/audio/voiceover/music details; verified actual judging result. The repo page exposed top-level files and README but the attempted source checkout failed for lack of space.
- **Version drift risk:** current README and older `hackathon.md` describe different counts/features (current README claims 13 tables/17 components, while build log snapshots earlier implementation and reports other counts). Forensics must pin claims to a commit/revision before treating them as equivalent.

## Cross-project comparison (evidence-weighted)

| Dimension | RecallReady | Parallel | PlusOne | OurSpaces |
|---|---|---|---|---|
| Human story | Product safety for household purchases | Team learning coverage at conferences | Wedding planning admin | Group memory / collaboration |
| Core technical differentiator | Safety matching + household workflow | Constraint optimizer + disruption repair | Evidence-grounded vendor research + email workflow | Realtime canvas + email/crawl inputs |
| AI role | Product extraction | Extraction, scoring, intent, brief | Research planner/extractor, drafting, assistant | Filing, question generation, grounded ask (README) |
| Deterministic boundary | Model/brand matching, access, resolution | Scheduling solver, revision and evidence guards | Approval, budget, source checks, role controls | Typed Convex mutations/realtime; code details not verified |
| Durable state | Inventory, matches, runs, events | Plans/revisions, replies, notes, sends | Wedding/vendor/quote/thread/workflow state | Space/widget/messages/presence/streams |
| Adaptive loop | No recurring monitor in archive | Reparse → detect stale → repair → get acceptance | Follow-up/quote workflows; no full vendor negotiation loop confirmed | Recap/refresh/crawl workflows claimed |
| Failure evidence | Small focused unit/backend tests | Broad adversarial and optimizer tests | Data-quality experiments, no test suite found | UNKNOWN from inspected materials |
| External side effect | Safety email | Assignment, cover request, brief emails | Vendor outreach / follow-up / RSVP | Email classification/reply |
| Main evidence gap | Recurring recall scans absent; submission checkboxes pending | Simulated conference narrative is disclosed; verify live records | Experiments are author-run, tests absent | README claims need pin-to-commit/source verification |

## What the evidence supports

1. “Technicality” is not feature count. Parallel's optimization and repair matter because session collisions, coverage, and change cost are the actual job. PlusOne's durable workflow and approval boundary matter because vendor research and communication take time and can create unwanted side effects. OurSpaces' database breadth is relevant where the product has many concurrently changing shared objects. RecallReady needs durable monitoring because persistent follow-up is its promise.
2. Strong projects make state and evidence legible: sources, exact identifiers, revisions, pending/failed states, activity, reason fields, and public run paths all make review easier.
3. The user's RecallReady architecture is already substantive: typed schema, household access control, signed webhook, deduplication, realtime reads, deterministic matching, and evidence records. The primary gap found is a missing product loop and proof/evaluation around it, not simply “more AI” or “more APIs.”
4. A source archive proves code and documentation exist. It does not prove production success, social engagement, submission completion, or an award. Those require current external records or event artifacts.

## Full subsystem inventory

`Unknown` means the available files do not establish the mechanism; it does not mean the mechanism cannot exist.

| Subsystem | RecallReady | Parallel | PlusOne | OurSpaces |
|---|---|---|---|---|
| Frontend | Vite + React + TypeScript | Vite + React + TypeScript | Vite + React + TypeScript + Tailwind v4 | README: Vite + React + TypeScript |
| Backend/database | Convex functions + Convex database | Convex functions + Convex database | Convex functions + Convex database | README: Convex |
| Authentication | Browser session token; household ownership checks | No user account; opaque link is access key; risk noted in build log | Convex Auth; wedding membership roles | README current: silent anonymous Convex Auth + email-code join; old build-log snapshot says no auth |
| Models/API | OpenAI Responses API, `gpt-5-mini`; Firecrawl; AgentMail REST/webhook | OpenAI structured-output client; Firecrawl component; AgentMail REST/webhook; Svix signatures | AI SDK OpenAI provider; `gpt-5.6-luna`/`gpt-5.6-terra` in build log; Firecrawl SDK; AgentMail client/webhook | README: Convex AI Gateway/OpenAI; Firecrawl + AgentMail. Model details differ by README/build-log version; see AI table below |
| Agent/tool design | No LLM tool loop found; extraction action + deterministic logic | No unrestricted agent; multiple structured model tasks coordinated by application/Convex workflows; deterministic solver | Wedding-scoped assistant with limited tools; separate email agent/reply workflow; exact total tool surface not established | README: `@convex-dev/agent`, threads, RAG; source-level tool definitions unavailable |
| Background work | `sourceRuns`; scheduler language in docs; cron module empty; no confirmed recurring source job | Durable workflow, bounded scoring workpool, scheduler, three crons claimed in build log | Durable workflows, workpool, hourly follow-up cron | README: workflow, workpool, batch worker, crons and scheduled actions |
| Event/webhook/queue | Signed AgentMail HTTP action; inbound event dedup; no separate queue identified | Signed AgentMail webhook; durable event rows; workpool/retry; outbound idempotency | Signed AgentMail webhook; first-touch claim/dedup; workflows/workpool | README: inbound dedup, webhook, refresh queue; implementation unavailable |
| State management | 8-table normalized Convex schema; realtime; household event/run state | 19-table schema in code/log; plan revision/frozen state; activity and provider records | 18-table schema in build log; weddings/events/vendors/threads/messages/quotes/budget state | README: 13-table current state description; typed 33-arm widget union, presence and streams |
| External/sponsor role | OpenAI extracts; Firecrawl fetches notices; AgentMail ingests/sends; Convex persists/syncs | OpenAI extracts/scores/parses/synthesizes; Firecrawl ingests/monitors agenda; AgentMail communicates; Convex persists/orchestrates | OpenAI drafts/extracts/answers; Firecrawl researches vendor websites/reviews; AgentMail sends and receives; Convex workflows/state/hosting | README: OpenAI files/answers, Firecrawl enriches/crawls, AgentMail inbox, Convex realtime backend |
| Search/retrieval | Convex full-text product search; no vector/RAG | No vector/RAG identified; Firecrawl scrape/crawl; optimizer indexes in memory | Firecrawl search/map/scrape; no vector/RAG identified | README: FTS + vector index, `ctx.vectorSearch`/RAG |
| Structured data pipeline | Strict 4-field receipt schema; official recall records; deterministic identifier match | Typed agenda/reply/scoring/brief schemas; timezone normalization, confidence fields, solver input matrices | Structured search/reply/quote outputs; currency/source validation; experimental quality data | README: typed widgets and AI-filed records; details unverified |
| Evaluation | Matcher unit tests and backend tests; no corpus-level recall/precision eval identified | Solver brute-force/property/determinism tests; build log claims 409 tests; not executed here | Measured Firecrawl/review pipeline scripts with source spot-checks; no unit test files/script in package | Unknown from public README/build log available here |
| Caching/rate limits | Unknown; no cache/rate limiter identified in inspected files | Action retrier and rate limiter components | Workflow retry/batch caps; general cache/rate limiter unknown | README claims action-cache and rate-limiter components |
| File/storage | Convex storage not identified | Storage not identified in inspected schema/config | Convex file storage for reply attachments and inspiration images | README says uploaded photos use Convex file storage |
| Deployment | Convex static hosting at `*.convex.site` | Convex static hosting at `*.convex.site` | Convex static hosting at `*.convex.site` | README: Convex static-hosting component |
| Observability/evidence | `events`, `sourceRuns`, inbound status/error, health route; no external monitoring identified | Activity records sponsor/duration, scoring status, plan objective/bound/nodes, source evidence, run pages | Activity log, workflow steps/research progress, source URLs and raw evaluation JSON | README: live stats/stream state; other observability unverified |
| Error handling | webhook status/error fields; provider errors throw; empty cron means no recurring recovery | bounded exact search + fallback; stale/frozen guards; action retries; parse states; adversarial tests | workflows retry by default; per-stage catches; follow-up cap and human escalation; no unit suite identified | README claims retry/cache/rate-limit components; code behavior unknown |
| Security controls | signed timestamped webhook, session/household ownership checks, server-side keys, demo read-only paths | webhook signature checks, opaque link tokens, frozen writes, internal functions, rate limiting/privacy tests; no conventional auth | role checks, Svix signatures, manual send approval, sender routing, scoped writes | README claims anonymous identity, optional code join, webhook verification/dedup and rate limits; source unverified |
| Testing architecture | Vitest + `convex-test`; 2 test files; browser e2e script declared in package | Vitest; 57 test files (README/log claims 409 tests); optimizer, Convex, email, agenda, adversarial suites | No test script/files found in archive manifest; Firecrawl eval scripts and data artifacts exist | Unknown; not locally inspected |

## Per-project AI contract inventory

| AI question | RecallReady | Parallel | PlusOne | OurSpaces |
|---|---|---|---|---|
| Why use AI? | Messy purchase email/product text is unstructured | Agendas, goal relevance, replies and takeaways are semantic | Natural-language needs, messy vendor webpages/emails, personal drafting | Flexible email classification and conversational queries (README claim) |
| Input → output | Receipt text → strict product/name/brand/model/retailer JSON | Webpage → session schema; session+goal → relevance/reason; email → intent/confidence/quote; notes → sourced brief | Wedding context/query/pages → vendor search plan/cards; messages/PDFs → quote/reply; context → draft/assistant output | Board/email/context → widget/answer (README; exact schema unavailable) |
| State/action effect | Creates inventory; matcher decides alert deterministically | Scores feed optimizer; guarded intent updates constraints; brief is persisted/delivered | Vendor cards/quotes/budget, drafts, limited assistant actions; outbound email requires confirmation | Email filing and persisted RAG/thread state (README) |
| Tools, result reaction | Provider calls are application actions; no LLM tool loop found | Application-controlled APIs; result enters solver/workflow; repair responds to new constraints | Assistant tool proposals initiate search/add need; workflow steps inspect Firecrawl/OpenAI results | `@convex-dev/agent` listed, tool set unknown |
| Retry/recovery/replan | Webhook dedup, status/error; no recurring scan or documented LLM retry policy confirmed | Durable workflow/retries; invalid replies can remain pending; constraint revision triggers deterministic replan | Durable retries; per-step fallback; follow-up cap/escalation; manual approval | README claims retries/workflows; replan details unknown |
| State/constraints | Household/product/source/match IDs; exact model/brand rules | Current plan revision, time conflicts, preferences, pins, coverage objective, bounded exact search | Wedding/event/budget/vendor slots/role and outreach approval; source-grounded pricing | Space/widget/member/message state; schema claims from README |
| Wrong-output behavior | required fields checked; bad output errors; no proven broader ambiguity flow | schemas/confidence/source validation; guarded state transitions; invalid takeaway can remain pending | schema + plausibility/source handling; review before send; unknown cases remain a product risk | unknown beyond README claims |
| Evaluation | small matcher/backend tests; no model quality dataset found | unit/property/brute-force/adversarial tests; reported count not executed | empirical source coverage/rating eval with raw artifacts; other evaluation unknown | unknown |

These tables intentionally separate **code-confirmed**, **repository-claimed**, and **unknown**. They are a map for the next verification pass, not a substitute for running a clean build or checking current deployments.

# UW Hackathon Rule-to-Engineering Map

The event page does not publish a weighted judging rubric. The table maps its explicit rules and submission instructions to product behavior and proof. Additional competitive dimensions come from Hackathon Build Standard V2, not official scoring claims. [Official event page](https://unusualwhales.com/information/2026-unusual-whales-hackathon)

| Rule / likely reviewer question | Engineering requirement | Implementation artifact | Demo evidence | Risk of losing confidence |
|---|---|---|---|---|
| Project must use UW API | UW API data must participate in the core evaluation, not only appear in a citation | `uw/` adapter; typed source IDs; documented direct endpoint calls | Show request retrieval metadata and resulting evidence-linked state | Mock-only or generic market API under a UW logo |
| Build anything on UW API | Deliver one concrete user result | Thesis creation to state transition, and evidence receipt | Start from thesis and show invalidation / indeterminate due to changed input | Broad dashboard with no user outcome |
| Trial keys acceptable | MVP must fit and disclose trial constraints | Endpoint entitlement matrix, usage budget, `.env.example` | Live key test or clearly labeled offline replay | Assume endpoint access without key proof |
| MCP + AI recommended, optional | If used, it must perform meaningful bounded work and disclose exact role; direct REST is allowed | AI schema/version; exact tool/endpoint list | Show proposal validation and evidence-bound explanation | Claim an agent when only one prompt/API response exists |
| Demo video OR images required | Make a truthful, coherent proof path; comply with UW data rights | Demo script and redacted/synthetic public evidence mode | One-minute workflow and repo replay | Expose restricted data or stage simulation as live |
| Short description 1–3 sentences | Product story must be understandable in one sentence and match functioning code | `README.md`, submission text | First 30 seconds explain thesis lifecycle | Marketing claims exceed hard promise |
| Endpoint list required | Inventory exact routes actually called | README endpoint table + adapter code | Endpoint call visible in app trace / dev log | Claim endpoints not wired or unavailable on trial |
| MCP/agent disclosure required | State yes/no and explain actual role | README AI and integration section | Show AI proposal and validation | Vague “agentic AI” claim |
| Other tools/libraries required | List real dependencies and jobs | Architecture/setup docs | Repo source confirms | Unused tech name-dropping |
| Repo/private repo or files | Reproducible project and no secrets | README, `.env.example`, lock file, fixture, license and data policy note | Fresh local startup/replay | API key in source, broken setup, no runnable path |
| UW endpoints are the sponsor integration | UW must be materially indispensable | Data adapter and explainable source mapping | Remove/swap UW source and core observation is absent | UW is only enrichment on generic AI product |
| No official detailed points published | Do not invent weighting; prioritize strong product, technical depth and proof transparently | This mapping and discovery memo | Reviewer sees proof promptly | Imply unofficial categories are official rubric |

## Claim-to-proof matrix for selected concept

| Claim | Working behavior required | Machine evidence | Demo moment |
|---|---|---|---|
| “Turns a thesis into a measurable test” | AI outputs schema-bound proposal, user confirms, deterministic validator rejects unsupported fields | Schema version + validated test definition | Plain-language input becomes visible condition list |
| “Uses UW evidence” | Direct UW call returns and normalizes actual event data | Source ID, endpoint identifier, event/received timestamps, sanitized status | Show source record linked to evaluated condition |
| “Tracks changing evidence” | New/corrected event triggers idempotent recomputation | Event ledger + before/after status and rule version | New input moves state or causes `indeterminate` |
| “Explains why status changed” | Explanation references only evaluator output and valid source IDs | Citation-ref validation output | Expand condition-level transition trace |
| “Replay is reproducible” | Same snapshot/rule/evaluator produces same output | Replay manifest and deterministic output hash | Rerun replay, show matching result |
| “Measures historical follow-through” | A time-bounded point-in-time cohort is evaluated against stated baseline | Sample count, exclusions, outcome metric, uncertainty and split boundaries | Cohort result with limitations visible |
| “Handles bad data” | Stale/incomplete records cannot preserve a confident status | Fault case and `indeterminate` reason | Introduce a data gap/duplicate and show detection/recovery |

## V2 gate status

- Hardest promise: specified in `UW_SELECTED_CONCEPT.md`; not yet implemented.
- Operational depth: design includes durable thesis/event state and reevaluation; demo must show a second event.
- Evidence: source lineage and replay manifest designed; trial/API terms remain open.
- Competitive loop: idea rejects ordinary dashboards/chatbots and maps UW product overlap.
- Gate result is discovery pass only; implementation proof does not exist yet.

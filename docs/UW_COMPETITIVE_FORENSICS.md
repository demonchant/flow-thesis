# UW Competitive Forensics

**Research date:** 2026-10-03. Public search is incomplete; the event's Discord project forum may contain unindexed entries. Every statement below is tagged by evidence level.

## UW's own products and displacement map

| Existing capability | Confirmed surface | Consequence for our design |
|---|---|---|
| Options-flow feed | Live feed, filtering, trade details, saved trades, live pause/resume, display/chart tooling | A prettier flow viewer is not a differentiated project. |
| Flow Alerts | Rule-based alerts on option tape; alert details can return constituent trades | “Large unusual flow” notification is directly replicated by UW. |
| Custom alerts | Public docs list alert configurations, filters and query grammar | A configurable alert bot is a thin product layer unless it has a deeper state/evaluation workflow. |
| Market analytics | Market/sector/ETF tide, Greeks/GEX, options pulse, net flow, screeners, darkpool, volume levels | Generic market dashboard and sentiment chatbot overlap heavily. |
| Contract analysis | Historical/intraday contract data, volume profiles, multi-leg identification and trade-stance ranking | Contract ranking or standalone option setup selection duplicates product/API capability. |
| AI/MCP | Official 200+ tool MCP plus prompts such as ticker analysis and daily market research | Natural-language data lookup and synthesized ticker analysis are not novel. |
| Trial/API examples | Official starter alert bot supports polling, LLM enrichment, webhooks, config hot reload, replay and noise probe; examples show WS-to-DuckDB/Parquet | “API + LLM + notification” and basic ingestion pipelines are established starting points. |

Sources: [UW Options Flow guide](https://docs.unusualwhales.com/features/2-options-flow/), [API endpoint catalog](https://api.unusualwhales.com/docs/llms.txt), [official MCP](https://github.com/unusual-whales/unusual-whales-official-mcp), [starter alert bot](https://github.com/unusual-whales/starter-alerts-bot), [API examples](https://github.com/unusual-whales/api-examples).

## Public project/repository landscape

| Project | Confirmed from public artifact | Competitive lesson | Unknown |
|---|---|---|---|
| [UW API examples](https://github.com/unusual-whales/api-examples) | Official annotated scripts/notebooks; includes WS ingestion to DuckDB and partitioned Parquet | Direct streaming + durable analytical storage is already shown in starter material; add a domain workflow/evaluation on top | Whether examples correspond to hackathon entries: no |
| [UW starter-alerts-bot](https://github.com/unusual-whales/starter-alerts-bot) | Typed flow polling, optional AI context, multi-sink delivery, replay, hot reload, request/noise safeguards | Generic alert + LLM + webhook is especially weak differentiation | Adoption or hackathon placement: unknown |
| [Official UW MCP](https://github.com/unusual-whales/unusual-whales-official-mcp) | Official MCP with 200+ market-data endpoints; relies on API key; excludes WebSockets | MCP integration alone is not a moat; sponsor data access needs a product-specific system layer | Exact tool set by a trial key: unknown |
| [Community MCP by phields](https://github.com/phields/unusualwhales-mcp) | 33 tools across 12 categories; thin direct API access; retry/error handling described | Tool wrappers are useful infrastructure but not a novel end-user solution | Current maintenance/runtime quality not exhaustively audited |
| [Trading Agent (OSSMafia)](https://github.com/OSSMafia/trader-bot) | Public repo describes PydanticAI, Temporal durable execution and UW MCP with Alpaca paper trading/risk controls | A trading agent is a known direction; execution claims introduce financial and safety risks. Avoid autonomous trading. | Independently verified behavior/test quality not established from search snippet |
| Community videos/articles on flow | UW itself publishes flow-alert walkthroughs and detailed interpretation education | A single-flow explainer risks duplicating UW education and still faces open/close uncertainty | Event submission status unknown |

No public entry for this specific hackathon was found in indexed search during this research. This is **unknown**, not evidence that no competitors exist. The official rules point to a Discord forum that search engines may not index. Before final review, inspect the actual forum and public links the user supplies.

## Competitive dimensions

### What a normal UW dashboard does

It displays/sorts real-time and historical options activity, offers filters and custom alerts, shows market-context views, and presents research data to the user. Reproducing those surfaces adds convenience but little underlying capability.

### What a generic market chatbot does

It answers a question by retrieving a few UW endpoints and narrating the result. UW's official MCP explicitly offers the same raw capability. A chat interface does not itself provide durable user hypotheses, versioned evidence, deterministic rules, outcomes or recovery.

### Proposed distinction

Flow Thesis Ledger starts with the user's own falsifiable claim, compiles it into a constrained test definition, saves a versioned observation policy, and maintains a state history: `draft → monitoring → supported / weakened / invalidated / indeterminate → closed`. Each transition points to raw UW record IDs, freshness and rule versions. A retrospective cohort/replay shows the observed behavior of that rule against a baseline, with limitations. AI can help clarify and structure the thesis and write a source-grounded explanation, but deterministic code decides status and score.

**Moat candidate:** reproducible point-in-time event reconstruction and thesis-version evaluation that prevents look-ahead leakage, deduplicates clustered flow alerts and carries source lineage through every state transition. This is more than an API call and creates an auditable user outcome. It is only a moat if implemented and measured.

## Product displacement and differentiation table

| Proposed feature | Already in UW? | Decision |
|---|---|---|
| Flow feed / alert filters | Yes | Do not build as a primary feature. |
| “AI explains this alert” | UW plus official bot example makes the pattern established | Only allow a cited explanation within the saved-thesis state lifecycle; AI cannot label signal validity alone. |
| Market context view | Yes, many endpoints/products | Ingest only as structured evidence for a specific test. |
| User-defined alert | Yes | A user thesis must express multiple falsifiable conditions, track both supporting and contradicting observations, preserve versions, compare replay outcomes, and show invalidation reason; otherwise this is merely an alert wrapper. |
| Generic historical backtest | The hackathon permits it and API supplies historical data; product overlap cannot be fully determined from public materials | Keep the contribution focused on bias-aware event cohort/replay and per-thesis evidence; no profitability claim. |
| Thesis-state ledger with source-linked transitions | Not located in inspected UW capabilities | Candidate product gap; still needs direct confirmation from UW products/support and broader competitor search. |

## Competitive risks and response

1. **Could be described as an alert bot.** Make the visual center the thesis, condition graph, counter-evidence, version history, cohort result and transition trace—not a live alert stream.
2. **Could overclaim causality/prediction.** Use “observed association” and “state under this rule,” never “UW signal predicts returns.” Include matched baselines and disclose costs, fill/slippage, multiple testing and survivorship limitations.
3. **Could overlap with custom UW alerts.** Require at least two explicit conditions and persistence/outcome evaluation; run the anti-wrapper test on actual implemented behavior.
4. **Could be difficult to demonstrate with trial data.** Keep an offline historical replay fixture clearly labeled and allow live direct API retrieval when access is available. Do not present fixture results as live.
5. **Terms may restrict public data sharing.** Resolve the contest/demo exception or use entrant-controlled local execution with public redacted proof.
6. **No indexed hackathon entries found.** Competitor ranking remains unknown until the forum is checked; do not claim unique or first.

## Competitive judgment

Based on inspected artifacts, strongest foreseeable entries will likely include live data, MCP/AI and attractive dashboards. A project that merely uses those features is easy to reproduce. Flow Thesis Ledger can separate itself by showing one saved thesis move from a concrete evidence state to an explained, rule-verified invalidation, then demonstrating that a point-in-time replay reproduces the same transition. Whether that is stronger than undiscovered submissions is unknown until the event forum is inspected.

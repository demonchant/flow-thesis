# Unusual Whales Hackathon: Discovery Record

**Research date:** 2026-10-03  
**Status:** Discovery complete; selected concept passes the product/technical gate subject to API-key smoke check and written clarification of data-display rights for the required public demo. The deterministic local core and synthetic replay have since been started; live UW integration remains unverified.

## Hackathon summary

The official event page says “Build anything on the Unusual Whales API,” allows dashboards, alerts, backtests and bots, recommends MCP with an AI agent, accepts API trial keys, and describes a one-month build window. Submission requires a GitHub repo, a Discord thread titled `Hackathon1: {{project title}}`, 1–3 sentence description, demo video or images, UW endpoint list, MCP/agent disclosure, other tools, files/repo, and local run/API-key instructions. Prizes listed are 1,000 USDC, 600 API credits and 400 API credits for first through third, with an optional product feature. The page does not expose a dated start, deadline, or detailed weighted judging rubric. Those are unknown and should be confirmed in the event channel. [Official rules](https://unusualwhales.com/information/2026-unusual-whales-hackathon)

**Operating implication:** there is no published technical rubric to optimize numerically. We use the event’s explicit UW API requirement and submission checklist, then apply V2’s product, depth, evidence, reliability, demo and competitive gates without claiming those are official weighted categories.

## Official sources inspected

| Source | What it establishes | Confidence/limit |
|---|---|---|
| [Hackathon page](https://unusualwhales.com/information/2026-unusual-whales-hackathon) | Eligibility, one-month duration, broad format, prizes, submission fields | Official; no date cutoff or scoring weights shown |
| [API docs index](https://api.unusualwhales.com/docs) and [LLM docs catalog](https://api.unusualwhales.com/docs/llms.txt) | API categories, endpoint links, bearer auth, REST/WebSocket/MCP references | Official; docs change over time |
| [OpenAPI YAML](https://api.unusualwhales.com/api/openapi) | Official spec URL identified, but this environment could not retrieve/parse the YAML (network failure / browser internal error) | **Not independently inspected**; do not claim schema-level validation |
| [Official MCP page](https://unusualwhales.com/public-api/mcp) and [official MCP repository](https://github.com/unusual-whales/unusual-whales-official-mcp) | Remote MCP endpoint is `https://api.unusualwhales.com/api/mcp`; bearer API key; 200+ tools/endpoints advertised | Official repository; the live connected tools are not available in this Codex session |
| [Pricing / trial](https://beta.unusualwhales.com/pricing?product=api) | Basic API $150/mo after a 7-day trial; 40k daily requests, 2-year history, listed realtime/WS capabilities; commercial plans from $625/mo billed annually | Current public pricing snapshot; confirm exact scope for account/key |
| [API Terms](https://unusualwhales.com/api-terms-of-service) | Individual/non-professional API is personal-use only; redistribution includes derived data and can revoke access | Official and material; public demo/media may need explicit permission or appropriate license |
| [Official API examples](https://github.com/unusual-whales/api-examples) | WebSocket collection and DuckDB/Parquet buffering examples | Official examples; not a turnkey persistent product |
| [Starter alerts bot](https://github.com/unusual-whales/starter-alerts-bot) | Flow polling, optional LLM enrichment, webhook delivery, replay mode, configuration reload and API-cost safeguards already exist as a starter pattern | Official repo; means “flow alert + AI + notification” is not novel |

UW documentation says requests use `https://api.unusualwhales.com` and `Authorization: Bearer <API_KEY>`. Its docs advertise 100+ endpoints and real-time/historical data. Endpoint catalog includes flow alerts, alert constituents by ID, option trade tape, multi-leg trades and legs, historical/intraday option-contract data, market tide, options pulse, Greeks/GEX, earnings, darkpool, SEC/news, congress and other categories. [API docs catalog](https://api.unusualwhales.com/docs/llms.txt)

## Access, cost and policy findings

- The hackathon explicitly accepts API trial keys. Public pricing describes a 7-day API trial, then Basic at $150/month with a published 40,000 requests/day and 2-year historical lookback. It describes Advanced at $375/month and a business/commercial plan from $625/month billed annually. Access to a specific endpoint, WebSocket channel, event history or MCP tool still needs a real key smoke check; do not infer entitlements from marketing copy alone. [Pricing](https://beta.unusualwhales.com/pricing?product=api)
- The official API terms state individual/non-professional use is personal use and that redistribution includes derived data. A publicly accessible hosted demo, screenshots, video, event artifacts or deployment could expose derived market data. Ask UW/event organizers in writing what the hackathon permits, or design a local-key demo that displays live data only to the entrant and uses redacted/synthetic public screenshots. This is a release condition, not a reason to conceal the limitation. [API terms](https://unusualwhales.com/api-terms-of-service)
- API usage counters reportedly appear in successful response headers, but a definitive trial quota or duration beyond the public seven-day trial was not established. Keep requests low, use cursors/caching, display usage, and re-check the actual key/account. **Trial quota for this project: unknown.**
- UW's flow-alert WebSocket page says personal WebSocket access is only available on the Advanced plan. Treat trial/Basic flow-alert streaming as unavailable unless UW confirms the account has an exception. MVP therefore uses conservative REST polling and reports its freshness interval; no real-time claim. [Flow-alert WebSocket docs](https://api.unusualwhales.com/docs/websocket/flow-alerts)
- The MCP documentation page is at `https://unusualwhales.com/public-api/mcp`; the actual authenticated remote MCP server is `https://api.unusualwhales.com/api/mcp`. It uses the API bearer key. Official repo advertises 200+ market-data endpoints and analysis prompts, and states WebSocket channels are intentionally not exposed. [MCP setup](https://github.com/unusual-whales/unusual-whales-official-mcp)
- UW links an agent skill at `https://unusualwhales.com/skill.md`, but this runtime could not retrieve its text through the available browser. No UW MCP server/tools or UW-specific skill are configured in the current Codex session; the remote MCP is not connected. The direct API docs instructions in `llms.txt` and official MCP README were inspected.
- The Flow Alerts endpoint returns time-bounded alert rows; its docs state the 14-day lookback cap on `/api/alerts` (custom alerts) does not apply to Flow Alerts. Detailed alert-by-ID returns constituent trades and may paginate with `has_more`/`older_than`. Actual historical availability still depends on entitlement and smoke check. [Flow Alerts](https://api.unusualwhales.com/docs/api/option-trade/flow-alerts), [Flow Alert by ID](https://api.unusualwhales.com/docs/api/option-trade/flow-alert-by-id)
- The Flow Alerts operation exposes many filter parameters and describes defaults (including an `all_opening` filter). The adapter must send intentional, explicit filters and document their semantics; relying on implicit defaults could silently bias the evidence cohort.
- This Codex runtime has no configured Unusual Whales MCP tools or skill, and no configured UW-specific API connector. The MCP is available as an external official service after user-key configuration; it is not currently connected here.

## Existing UW capability displacement check

UW already provides a desktop/mobile options-flow feed, flow alerts and saved alerts, custom alert configurations, real-time flow, options screeners, Market Tide, darkpool/volume levels, Greeks/GEX, an options trade-stance ranking endpoint, API examples including replay mode, and a 200+ endpoint official MCP with research prompts. Its flow explanations explicitly caution that trade side and open/close intent have uncertainty; an options trade may be a leg of a multi-leg position. [Options Flow guide](https://docs.unusualwhales.com/features/2-options-flow/), [API docs catalog](https://api.unusualwhales.com/docs/llms.txt), [official MCP](https://github.com/unusual-whales/unusual-whales-official-mcp)

Consequently, do not build a generic flow dashboard, stock/options chatbot, alert bot, screener, contract ranking or narrative summary. Those capabilities are available directly or exemplified by UW. The viable gap is a user-owned, versioned hypothesis lifecycle: turn a specific thesis into explicit tests, track evidence and counter-evidence as state, evaluate the observed outcome against a baseline, and preserve an auditable record of how/why the thesis status changed.

## Official criteria translated to engineering

| Official requirement | Engineering response | Evidence / demo proof |
|---|---|---|
| Use UW API | Direct typed UW REST ingestion for flow and market context; show source endpoint and retrieval time | Request/response metadata with secrets removed; endpoint list; source-linked event record |
| Any format allowed | Choose one narrow user workflow, not a general-purpose dashboard | One-minute thesis create → evidence update → invalidation/recovery story |
| Demo clip or screenshots required | Ensure a reproducible, truthful demo without redistributing restricted UW data | Clarification from UW or redacted/synthetic public proof; private local live-key walkthrough |
| Endpoint list and MCP/agent disclosure | Document exact API routes, whether direct REST or MCP, and exact AI role | README and submission draft |
| Repo and local setup | Safe `.env.example`, offline replay fixture, reproducible launch | Clean-machine setup notes; no API key in source/history |
| UW benefit/integration | UW’s options-flow event detail and time series drive hypothesis evaluation | Demonstrate the before/after analysis fails when those observations are removed |

## Research limits / open questions

1. Official OpenAPI YAML URL could not be downloaded in this environment. However, the official generated operation pages for Flow Alerts, Flow Alert by ID and the flow-alert WebSocket were inspected, including route, parameters, response shape and access notes. The entire YAML and all candidate endpoint schemas were not independently parsed. Before expanding implementation, retrieve the YAML successfully and validate every selected route/field against it.
2. No official weighted judging rubric, start date or final submission deadline was visible in the hackathon page. Confirm in Discord; until then, time feasibility is an estimate.
3. Trial credentials and exact trial limits are not available in this workspace; no secret was inspected or printed. Endpoint/WebSocket entitlements, rate limits and historical range must be smoke-tested with the entrant’s key.
4. Search found no indexed public submissions for this specific event beyond UW examples and generic public repositories. The Discord forum may contain unindexed competitors. “No competitor found” is not a uniqueness claim.
5. API terms and public demo requirements may conflict for data-derived content. Obtain a written interpretation before publicly displaying UW-derived values.

## Discovery outcome

Advance **Flow Thesis Ledger** as the selected concept, conditional on (a) verifying one Basic/trial-safe flow endpoint plus point-in-time market context and historical outcome data, and (b) resolving data display/licensing for the required public evidence. The concept is narrow enough to build in a month, and its technical value is the evidence lifecycle, point-in-time replay and versioned state rather than prediction or a trade recommendation. Full candidate scoring and architecture are in the adjacent UW documents.

# Flow Thesis Ledger

Flow Thesis Ledger turns a user-written options-flow thesis into bounded, deterministic conditions; ingests Unusual Whales Flow Alerts; stores normalized evidence and evaluations in SQLite; and tracks whether later observations support, weaken, invalidate, or leave the thesis indeterminate. The AI compiler proposes a structured draft. A person must approve read-only monitoring. It never places or activates trades.

## What works

- Reads UW `GET /api/option-trades/flow-alerts` and normalizes the account's observed `ticker`, option premium, underlying reference price at alert time, size, and sweep/multileg fields into typed events.
- Persists event versions, polling cursors, thesis activations, evaluation receipts, and state transitions in SQLite. Repeated observations are deduplicated and a full page is marked potentially truncated without advancing the cursor.
- Evaluates allow-listed numeric and boolean predicates deterministically. Missing required evidence produces `indeterminate`; it cannot silently count as support.
- Uses the OpenAI Responses API with strict JSON Schema output to compile the user's statement plus optional normalized evaluation evidence into an unactivated thesis draft. Local tests mock the API response and cover request construction, parsing, evidence validation, draft status, failure sanitization, and the activation guard.
- Replays saved live UW alerts in market-event order and recomputes the thesis state at each point using deterministic rules; each step exposes its source alert and reproducibility hashes.
- Includes an optional Unusual Whales MCP plugin and a remote server configuration using each user's local `UW_API_KEY`.

## Quick start

Requires Python 3.11+; the application and tests use the Python standard library.

```powershell
python -m unittest discover -s tests -v
python -m compileall -q flow_thesis_ledger tests
```

## Live UW pipeline

Set `UW_API_KEY` in the shell that launches Python. Never paste it into source, a command argument, screenshots, or a submission. The read-only verifier checks the list route and, when an ID is present, the alert detail route without printing response values:

```powershell
python -m flow_thesis_ledger.verify_uw
python -m flow_thesis_ledger.live_smoke
```

The verified account run returned HTTP 200 for `GET /api/option-trades/flow-alerts` and `GET /api/option-trades/flow-alerts/{id}`. The observed list schema uses `ticker` (not only `ticker_symbol`), string-valued premium fields, and numeric size. The normalizer and local fixtures cover those observed names/encodings. Run `live_smoke` from the credential-bearing shell to demonstrate a fresh live normalize → in-memory persist → deterministic evaluation path. See [UW evidence](docs/UW_EVIDENCE.md) for the exact evidence scope.

Compile a thesis (requires an OpenAI API key with available API credit):

```powershell
python -m flow_thesis_ledger.compile_thesis --statement "AAPL flow premium above my chosen threshold supports this thesis" --output .local/aapl-draft.json
```

Review the draft. Start read-only monitoring only after review:

```powershell
python -m flow_thesis_ledger.monitor .local/aapl-draft.json --approve --once
python -m flow_thesis_ledger.monitor .local/aapl-draft.json --interval 60
```

The first `--approve` is an explicit human confirmation, persisted by thesis ID/version. Subsequent runs can continue the approved monitoring session. Polling is foreground REST polling, defaults to 60 seconds, and stops on 401/403. State and receipts stay in `.local/flow-thesis-ledger.sqlite3`.

## Graphical live console

Launch the browser app from the same shell that has the server-side credentials:

```powershell
python -m flow_thesis_ledger.live_web
```

Open `http://127.0.0.1:8766`. The browser never needs or receives an API key. The app provides Overview, New Thesis, Evidence, Replay, and Settings screens; New Thesis loads ticker symbols from the current UW Flow Alerts page. A new thesis action retrieves live UW alerts, normalizes and persists matching records, creates a draft with either the no-cost deterministic rule compiler or the optional OpenAI structured-output compiler, and records the first deterministic evaluation. Review and explicitly approve read-only monitoring before polling. Replay steps through the actual live alerts saved for the current thesis in event-time order and recomputes the state at every step. It never substitutes a bundled example; with no saved live observations, it displays an empty state. Export evidence from the Evidence screen.

The console binds to localhost only and stores its SQLite ledger under `.local/`. API keys are read from the Python process environment; the app does not load or write them to `.env`. Settings distinguishes a key being present from an integration successfully responding. The shell that starts the app must inherit both credentials for the full live workflow. This repository does not include a public deployment or a shared multi-user UW data proxy.

The optional OpenAI request uses Responses API Structured Outputs with a strict JSON Schema so the result is application-ready and independently validated before it becomes a draft; see [official Structured Outputs documentation](https://developers.openai.com/api/docs/guides/structured-outputs). The deterministic mode instead applies the threshold entered in the UI; it does not infer rules from free text and makes no OpenAI request.

The current screen capture can be turned into a polished demo with the [video renderer](scripts/render_demo_video.py). It adds an animated title and section cards, subtle push-ins, transition swishes, ElevenLabs narration, and a quiet original music bed, while cutting the old error notices. From PowerShell in the repository root, run `./scripts/render_demo_video.ps1`; it reads an existing process key or the current user's environment setting without displaying it. The output is `artifacts/flow-thesis-demo.mp4`; the raw `1.mp4` capture is local-only and should not be committed. See [video edit notes](docs/DEMO_VIDEO_EDIT.md). The older recording walkthrough is documented in the [screen recording runbook](docs/DEMO_RECORDING_RUNBOOK.md).

## OpenAI and MCP setup

OpenAI integration remains implemented and wired. Deterministic mocked tests need no API charge. A live request previously returned HTTP 429 `insufficient_quota`, so successful model generation has not been verified; add account credit to exercise it live. Unit tests use isolated fixtures; the user-facing Replay page only accepts saved live UW events.

Codex MCP configuration is available in this repository as `plugins/unusual-whales/.mcp.json` and a user marketplace entry at `.agents/plugins/marketplace.json`. It points to the official hosted UW MCP server and resolves the user's `UW_API_KEY` from their environment. The plugin package includes an on-demand skill for other users; each needs their own UW API key and account entitlements. See [MCP setup and tools](plugins/unusual-whales/README.md).

## Hackathon submission information

- **Problem:** Options-flow evidence is easy to overinterpret and hard to track against a stated thesis as new observations arrive.
- **Outcome:** A versioned, auditable thesis status with supporting evidence and deterministic reasons; the AI drafts rules but does not decide market outcomes.
- **UW endpoints:** `GET /api/option-trades/flow-alerts`; `GET /api/option-trades/flow-alerts/{id}` (used by the safe verifier). The live monitor uses the first route. No write/trading route is used.
- **MCP / agent:** Yes, an optional Codex plugin connects to the official UW MCP endpoint. The product's thesis compiler is a bounded OpenAI structured-output workflow, not an autonomous trading agent.
- **Other tools:** Python standard library, SQLite, OpenAI Responses API.
- **Working images/demo:** `artifacts/` and [live recording runbook](docs/DEMO_RECORDING_RUNBOOK.md).
- **Run locally:** See [Quick start](#quick-start) and [Live UW pipeline](#live-uw-pipeline).
- **Configuration:** Environment variables only; no secrets belong in this repository. Trial access is route-specific and should be checked with `verify_uw`.

`.env.example` lists the supported variable names as an empty template; the app does not read `.env` files automatically. Set credentials through your shell or a local secret manager so they enter the process environment without becoming source files.

## Repository map

- `flow_thesis_ledger/` — API client, normalization/poller, deterministic engine, SQLite store, AI compiler, and live console with live-ledger replay.
- `tests/` — deterministic tests for normalization, persistence, polling, failures, AI response mocks, human approval, and live replay filtering.
- `docs/UW_EVIDENCE.md` — implementation and verification evidence with known limits.
- `plugins/unusual-whales/` — portable MCP plugin scaffold and safe tool catalog command.
- `artifacts/` — working product images for the hackathon post.

This is an evidence/research workflow, not financial advice, price prediction, or a trading system. Do not redistribute live or derived UW data; follow the [UW API terms](https://unusualwhales.com/api-terms-of-service).

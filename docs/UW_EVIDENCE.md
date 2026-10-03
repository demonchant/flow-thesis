# Flow Thesis Ledger: implementation and verification evidence

## End-to-end claim map

| Claim | Implementation | Verification evidence |
|---|---|---|
| UW Flow Alerts can be consumed with this account | `uw_api.py`, `verify_uw.py` | Account-run verifier reported HTTP 200 for list and detail routes; safe response shapes are captured without values in the report supplied by the account owner. |
| Live Flow Alert field names normalize correctly | `uw_ingest.py` | Tests use the observed `ticker`, `underlying_price`, `total_premium`, `total_size`, `total_ask_side_prem`, and `total_bid_side_prem` field names and string/numeric encodings. |
| Observations persist and duplicates are idempotent | `store.py`, `uw_ingest.py` | Unit tests cover duplicate writes, repeated polling, cursor ordering, and persistence after constructing a new store over the same SQLite file. |
| Deterministic evaluation is auditable | `engine.py`, `store.py` | Tests cover known predicate states, missing metrics → `indeterminate`, input/output hashes, and append-only evaluation receipts. |
| AI only creates a bounded thesis draft | `ai.py`, `compile_thesis.py` | Mocked Responses API tests inspect Bearer request construction, strict JSON Schema, `store=false`, parsing, field/evidence validation, draft status, and sanitized quota failure. |
| Monitoring needs human approval | `monitor.py`, `store.py` | Tests reject an unapproved draft, persist approval, and allow an already approved version to resume read-only monitoring. |
| Replay remains reproducible | `examples/thesis_replay.json`, `engine.py` | Regression test runs replay twice and confirms the `supported` → `invalidated` sequence and identical hashes. |
| The browser app exposes the end-to-end workflow | `live_web.py`, `live_console.html` | Local route smoke checks cover all five screens, the status API, SVG asset, and synthetic replay page; request checks cover malformed JSON and Host rejection. A successful live prepare action compiles a draft and records its initial deterministic evaluation. |
| Failure behavior does not expose secrets or provider payloads | `uw_api.py`, `ai.py`, `monitor.py`, `verify_uw.py` | Tests inject timeout, HTTP error, and OpenAI quota responses and assert sanitized public errors. |

## Live evidence reported by the account owner

From the PowerShell session with the user's configured UW credential:

- `GET /api/option-trades/flow-alerts`: HTTP 200; response contract `data` array; one row returned during verification.
- `GET /api/option-trades/flow-alerts/{id}`: HTTP 200; response had `alert`, `has_more`, and `trades` top-level fields.
- Observed alert summaries included `ticker` as a string, premium amounts as strings, and `total_size` as a number. Detail trade rows included string and numeric option fields.
- The `live_smoke` command is available to exercise live normalization → in-memory persistence → deterministic evaluation; no result for that command has been reported in the current session.

This confirms only the two routes tested for that account and time. It does not establish access to every UW route, quotas, MCP entitlements, or sustained uptime.

## Local suite

Run from the project root:

```powershell
python -m unittest discover -s tests -v
python -m compileall -q flow_thesis_ledger tests
```

The suite uses fake clients and mocked OpenAI responses; it does not require API credits or contact either service.

## Browser workflow

`python -m flow_thesis_ledger.live_web` starts the local graphical console at `http://127.0.0.1:8766`. The browser receives no credentials. The New Thesis action fetches the actual alert page, records only normalized events, compiles an OpenAI structured draft, then records its first deterministic evaluation. Human approval is required before monitoring; Poll invokes the UW endpoint and persists any evaluation/state transition. The Settings screen reports credential presence separately from a successful request. Offline replay remains marked synthetic. The UI is responsive and includes purpose-built SVG workflow/ledger illustrations rather than fabricated market screenshots.

Live UW access from the account owner’s earlier PowerShell verifier is evidence for the two endpoints and time recorded above. It is not evidence that a live browser prepare, OpenAI model call, or continuously running poll has succeeded. Those are verified only by successful completion of the corresponding action in the live app.

## Remaining external evidence

- The user account has no OpenAI API credit; live model generation is not verified. The implementation and mock suite are present.
- The connected Codex runtime needs a restart/reload before the newly configured UW MCP server appears in its dynamic tool list. The repository includes `plugins/unusual-whales/scripts/list_tools.py` for an exact, redacted `tools/list` query from a shell that already has `UW_API_KEY`.
- Hackathon entry still requires the owner to post the project in the organizer's Discord forum with this repository link and attach the included working screenshot(s) (or a demo clip).

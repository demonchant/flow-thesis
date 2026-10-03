# Unusual Whales Hackathon post draft

**Title:** `Hackathon1: Flow Thesis Ledger`

**What it does**

Flow Thesis Ledger turns a user's options-flow thesis into a reviewable set of deterministic rules, then records whether new Unusual Whales Flow Alerts support, weaken, or invalidate those rules. Each state change links back to normalized event evidence and reproducible evaluation hashes; AI drafts the rule proposal, and the user must approve read-only monitoring.

**Demo video (required before posting)**

Record the real live workflow using `docs/LIVE_DEMO_VOICEOVER.md`. The generated narration and caption files are in `artifacts/flow-thesis-live-voiceover.mp3` and `.srt`. The committed replay screenshots are synthetic regression evidence only; do not present them as live UW activity.

The images show the deterministic demo fixture only. They contain no real UW account data. Live flow ingestion is available via the read-only CLI path documented in the repository.

**Built with**

- UW endpoints: `GET /api/option-trades/flow-alerts`; `GET /api/option-trades/flow-alerts/{id}` for the safe live verifier.
- MCP / agent: The optional Codex plugin connects to the official Unusual Whales remote MCP server for development. The web application uses the UW REST API directly. Its thesis compiler is a bounded OpenAI structured-output workflow, not an autonomous trader.
- Other tools/libs: Python standard library, SQLite, OpenAI Responses API, Codex MCP plugin format.

**Files**

- GitHub: https://github.com/demonchant/flow-thesis
- No API keys are included. Configure `UW_API_KEY` and, for live thesis compilation, `OPENAI_API_KEY` in the local process environment.

**Run locally**

```powershell
python -m flow_thesis_ledger examples/thesis_replay.json
python -m flow_thesis_ledger.web examples/thesis_replay.json
python -m flow_thesis_ledger.live_web
python -m unittest discover -s tests -v
```

The live console opens at `http://127.0.0.1:8766`. Set `UW_API_KEY` and `OPENAI_API_KEY` in the server process environment before starting it. No keys are entered in the browser or included in this repository.

For read-only live UW endpoint verification, set `UW_API_KEY` in your local shell and run `python -m flow_thesis_ledger.verify_uw`. See the root README for monitoring and review-gated activation instructions.

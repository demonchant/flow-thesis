# Flow Thesis Ledger package

Project overview, setup, live endpoint evidence, AI compiler behavior, and verification commands are in the repository [README](../README.md) and [UW evidence record](../docs/UW_EVIDENCE.md).

This package contains the read-only UW client, live normalizer and poller, deterministic evaluator, SQLite ledger, live UW ledger replay, OpenAI structured thesis compiler, local console, and safe endpoint verifier. Replay reads saved live alert records only; it never loads example data. The system never submits a trade.

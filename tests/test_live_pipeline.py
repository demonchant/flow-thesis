from __future__ import annotations

import unittest
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.error import URLError
from unittest.mock import patch

from flow_thesis_ledger.ai import ThesisCompileError, ThesisCompiler
from flow_thesis_ledger.models import Condition, Thesis
from flow_thesis_ledger.monitor import prepare_monitoring
from flow_thesis_ledger.store import LedgerStore
from flow_thesis_ledger.uw_api import UWAPIError, UWClient, UWResponse
from flow_thesis_ledger.uw_ingest import FlowAlertPoller, normalize_flow_alerts
from flow_thesis_ledger.verify_uw import _safe_shape, check
from flow_thesis_ledger.__main__ import load_snapshot
from flow_thesis_ledger.engine import evaluate_snapshot, replay


class LivePipelineTests(unittest.TestCase):
    def test_normalize_flow_alert_with_known_fields(self) -> None:
        events = normalize_flow_alerts({"data": [{
            "id": "safe-id", "ticker": "AAPL", "created_at": "2026-10-03T10:00:00Z",
            "total_premium": "125000", "total_size": 42, "underlying_price": "$183.42",
            "total_ask_side_prem": "100,000", "total_bid_side_prem": "25,000",
            "has_sweep": True,
            "unexpected_private_field": "ignored",
        }]}, received_at=datetime(2026, 10, 3, 10, 0, 1, tzinfo=timezone.utc))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].ticker, "AAPL")
        self.assertEqual(events[0].fields, {
            "total_premium": 125000.0, "total_size": 42.0, "underlying_price": 183.42,
            "total_ask_premium": 100000.0, "total_bid_premium": 25000.0,
            "has_sweep": True,
        })
        self.assertEqual(events[0].mode, "live")

    def test_normalizer_omits_malformed_rows_and_requires_data_array(self) -> None:
        self.assertEqual(normalize_flow_alerts({"data": [{"ticker_symbol": "AAPL"}]}), [])
        with self.assertRaises(ValueError):
            normalize_flow_alerts({"unexpected": []})

    def test_empty_page_is_valid_and_missing_metrics_fail_indeterminate(self) -> None:
        self.assertEqual(normalize_flow_alerts({"data": []}), [])
        now = datetime.now(timezone.utc)
        events = normalize_flow_alerts({"data": [{
            "id": "missing-fields", "ticker_symbol": "AAPL", "created_at": now.isoformat(),
        }]}, received_at=now)
        self.assertEqual(events[0].fields, {})
        self.assertFalse(events[0].complete)
        thesis = Thesis("t", 1, "AAPL", "test", (
            Condition("c", "total_premium", "gte", 1, "support", "required metric"),
        ), ("total_premium",), 3600)
        self.assertEqual(evaluate_snapshot(thesis, events, evaluated_at=now).status, "indeterminate")

    def test_store_persists_cursor_and_deduplicates_identical_events(self) -> None:
        from flow_thesis_ledger.models import Event
        now = datetime(2026, 10, 3, tzinfo=timezone.utc)
        event = Event("uw", "one", "AAPL", now, now, "flow_alert", {"total_size": 2}, mode="live")
        store = LedgerStore(":memory:")
        self.addCleanup(store.close)
        self.assertEqual(store.append_events([event, event]), 1)
        self.assertEqual(store.poll_cursor("thesis", "AAPL"), None)
        store.set_poll_cursor("thesis", "AAPL", now.isoformat())
        self.assertEqual(store.poll_cursor("thesis", "AAPL"), now.isoformat())

    def test_poller_persists_before_advancing_cursor_and_marks_full_page(self) -> None:
        now = datetime(2026, 10, 3, 10, tzinfo=timezone.utc)
        thesis = Thesis("t", 1, "AAPL", "flow exceeds threshold", (
            Condition("c1", "total_premium", "gte", 1000, "support", "premium threshold"),
        ), ("total_premium",), 3600)

        class Client:
            def flow_alerts(self, params):
                self.params = params
                return UWResponse(200, {}, {"data": [{
                    "id": "a1", "ticker_symbol": "AAPL", "created_at": now.isoformat(),
                    "total_premium": 1500,
                }]})

        store = LedgerStore(":memory:")
        self.addCleanup(store.close)
        result = FlowAlertPoller(Client(), store, limit=1).poll_once(thesis)
        self.assertTrue(result["possibly_truncated"])
        self.assertEqual(result["inserted"], 1)
        self.assertIsNone(store.poll_cursor("t", "AAPL"))

    def test_repeated_poll_is_idempotent_and_uses_persisted_cursor(self) -> None:
        now = datetime.now(timezone.utc)
        thesis = Thesis("t", 1, "AAPL", "test", (
            Condition("c", "total_premium", "gte", 0, "support", "smoke"),
        ), ("total_premium",), 3600)
        class Client:
            calls = []
            def flow_alerts(self, params):
                self.calls.append(dict(params))
                return UWResponse(200, {}, {"data": [{
                    "id": "same-id", "ticker_symbol": "AAPL", "created_at": now.isoformat(),
                    "total_premium": 42,
                }]})
        client, store = Client(), LedgerStore(":memory:")
        self.addCleanup(store.close)
        poller = FlowAlertPoller(client, store, limit=5)
        first = poller.poll_once(thesis)
        second = poller.poll_once(thesis)
        self.assertEqual(first["inserted"], 1)
        self.assertEqual(second["inserted"], 0)
        self.assertEqual(len(store.load_events()), 1)
        self.assertIn("newer_than", client.calls[1])

    def test_persistent_state_survives_store_restart(self) -> None:
        now = datetime.now(timezone.utc)
        thesis = Thesis("persisted", 1, "AAPL", "test", (
            Condition("c", "total_premium", "gte", 0, "support", "smoke"),
        ), ("total_premium",), 3600)
        event = normalize_flow_alerts({"data": [{
            "id": "persist-me", "ticker_symbol": "AAPL", "created_at": now.isoformat(),
            "total_premium": 2,
        }]}, received_at=now)[0]
        with TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.sqlite3"
            first = LedgerStore(path)
            first.save_thesis(thesis, now.isoformat())
            first.append_events([event])
            first.set_poll_cursor(thesis.id, thesis.ticker, now.isoformat())
            evaluation = evaluate_snapshot(thesis, [event], evaluated_at=now)
            first.record_evaluation(evaluation, None)
            restarted = LedgerStore(path)
            self.assertEqual(len(restarted.load_events()), 1)
            self.assertEqual(restarted.poll_cursor(thesis.id, thesis.ticker), now.isoformat())
            self.assertEqual(restarted.latest_status(thesis.id), evaluation.status)

    def test_ai_review_notes_survive_store_restart(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.sqlite3"
            first = LedgerStore(path)
            first.save_thesis_notes("notes", 1, "Evidence summary", ["flow is not direction"], ["uw-alert-1"])
            first.close()
            restarted = LedgerStore(path)
            try:
                self.assertEqual(restarted.load_thesis_notes("notes", 1), {
                    "summary": "Evidence summary", "uncertainties": ["flow is not direction"],
                    "evidence_refs": ["uw-alert-1"],
                })
            finally:
                restarted.close()

    def test_uw_auth_header_is_bearer_and_route_is_read_only(self) -> None:
        class FakeResponse:
            status = 200
            headers = {}
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b'{"data": []}'

        captured = {}
        def fake_open(request, timeout):
            captured["authorization"] = request.get_header("Authorization")
            captured["method"] = request.get_method()
            captured["url"] = request.full_url
            return FakeResponse()

        with patch("flow_thesis_ledger.uw_api.urlopen", fake_open):
            response = UWClient("test-secret-never-logged", retries=0).flow_alerts({
                "limit": 1, "all_opening": "false",
            })
        self.assertEqual(response.status, 200)
        self.assertEqual(captured["authorization"], "Bearer test-secret-never-logged")
        self.assertEqual(captured["method"], "GET")
        self.assertIn("all_opening=false", captured["url"])

    def test_api_timeout_retries_are_bounded_and_safe(self) -> None:
        with patch("flow_thesis_ledger.uw_api.urlopen", side_effect=URLError("network detail")) as mocked:
            with patch("flow_thesis_ledger.uw_api.time.sleep"):
                with self.assertRaises(UWAPIError) as raised:
                    UWClient("never-print-this", retries=1).flow_alerts({"limit": 1, "all_opening": False})
        self.assertEqual(mocked.call_count, 2)
        self.assertTrue(raised.exception.retryable)
        self.assertNotIn("never-print-this", str(raised.exception))
        self.assertNotIn("network detail", str(raised.exception))

    def test_http_error_body_is_not_exposed(self) -> None:
        error = HTTPError("https://api.unusualwhales.com/api/option-trades/flow-alerts", 403,
                          "forbidden", {}, BytesIO(b"sensitive response body"))
        with patch("flow_thesis_ledger.uw_api.urlopen", side_effect=error):
            with self.assertRaises(UWAPIError) as raised:
                UWClient("never-print-this", retries=0).flow_alerts({"limit": 1, "all_opening": False})
        self.assertEqual(raised.exception.status, 403)
        self.assertNotIn("sensitive response body", str(raised.exception))

    def test_compiler_validation_rejects_unsupported_fields(self) -> None:
        invalid = {
            "ticker": "AAPL", "statement": "test", "summary": "test",
            "conditions": [{"field": "stock_price", "comparator": "gte", "threshold": 10,
                            "kind": "support", "description": "bad"}],
            "required_fields": [], "freshness_seconds": 900, "uncertainties": [],
        }
        with self.assertRaises(ThesisCompileError):
            ThesisCompiler._validate(invalid, thesis_id="x", version=1)

    def test_compiler_validation_returns_unactivated_draft(self) -> None:
        valid = {
            "ticker": "aapl", "statement": "AAPL flow thesis", "summary": "Mapped one rule",
            "conditions": [{"field": "total_premium", "comparator": "gte", "threshold": 100000,
                            "kind": "support", "description": "large premium"}],
            "required_fields": ["total_premium"], "freshness_seconds": 900, "uncertainties": ["flow is not direction"],
            "evidence_refs": [],
        }
        proposal = ThesisCompiler._validate(valid, thesis_id="draft", version=1)
        self.assertEqual(proposal.thesis.status, "draft")
        self.assertEqual(proposal.thesis.ticker, "AAPL")
        self.assertEqual(proposal.thesis.conditions[0].field, "total_premium")

    def test_compiler_builds_structured_request_and_parses_mocked_response(self) -> None:
        valid = {
            "ticker": "AAPL", "statement": "AAPL flow threshold", "summary": "Rule draft",
            "conditions": [{"field": "total_premium", "comparator": "gte", "threshold": 1000,
                            "kind": "support", "description": "premium condition"}],
            "required_fields": ["total_premium"], "freshness_seconds": 900,
            "uncertainties": ["Flow is not directional"], "evidence_refs": [],
        }
        captured = {}
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self):
                import json
                return json.dumps({"status": "completed", "output": [{"content": [
                    {"type": "output_text", "text": json.dumps(valid)},
                ]}]}).encode()
        def fake_open(request, timeout):
            import json
            captured["authorization"] = request.get_header("Authorization")
            captured["method"] = request.get_method()
            captured["timeout"] = timeout
            captured["body"] = json.loads(request.data)
            return FakeResponse()
        compiler = ThesisCompiler(api_key="mock-only-key", model="mock-model", timeout=3)
        with patch("flow_thesis_ledger.ai.urlopen", fake_open):
            proposal = compiler.compile("AAPL flow threshold", thesis_id="mocked", version=2)
        self.assertEqual(captured["authorization"], "Bearer mock-only-key")
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["timeout"], 3)
        self.assertEqual(captured["body"]["model"], "mock-model")
        self.assertFalse(captured["body"]["store"])
        self.assertEqual(captured["body"]["text"]["format"]["type"], "json_schema")
        self.assertTrue(captured["body"]["text"]["format"]["strict"])
        self.assertEqual(proposal.thesis.status, "draft")
        self.assertEqual(proposal.thesis.version, 2)

    def test_compiler_rejects_mocked_invalid_and_invented_evidence(self) -> None:
        import json
        valid = {
            "ticker": "AAPL", "statement": "AAPL flow threshold", "summary": "Rule draft",
            "conditions": [{"field": "total_premium", "comparator": "gte", "threshold": 1000,
                            "kind": "support", "description": "premium condition"}],
            "required_fields": ["total_premium"], "freshness_seconds": 900,
            "uncertainties": [], "evidence_refs": ["made-up-event"],
        }
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self):
                return json.dumps({"status": "completed", "output": [{"content": [
                    {"type": "output_text", "text": json.dumps(valid)},
                ]}]}).encode()
        with patch("flow_thesis_ledger.ai.urlopen", return_value=FakeResponse()):
            with self.assertRaises(ThesisCompileError):
                ThesisCompiler(api_key="mock-only-key").compile("AAPL flow thesis")

    def test_activation_requires_explicit_approval_and_only_enables_monitoring(self) -> None:
        thesis = Thesis("approval", 1, "AAPL", "user-reviewed statement", (
            Condition("c", "total_premium", "gte", 1000, "support", "premium"),
        ), ("total_premium",), 900, status="draft")
        store = LedgerStore(":memory:")
        self.addCleanup(store.close)
        with self.assertRaises(PermissionError):
            store.activate_thesis(thesis, human_approved=False, approved_at="2026-10-03T00:00:00Z")
        self.assertFalse(store.is_activated(thesis.id, thesis.version))
        activated = store.activate_thesis(thesis, human_approved=True, approved_at="2026-10-03T00:00:00Z")
        self.assertEqual(activated.status, "monitoring")
        self.assertTrue(store.is_activated(thesis.id, thesis.version))

    def test_monitoring_requires_and_persists_explicit_approval(self) -> None:
        thesis = Thesis("monitor-approval", 1, "AAPL", "reviewed", (
            Condition("c", "total_premium", "gte", 1000, "support", "premium"),
        ), ("total_premium",), 900, status="draft")
        store = LedgerStore(":memory:")
        self.addCleanup(store.close)
        with self.assertRaises(PermissionError):
            prepare_monitoring(thesis, store, approve=False, now="2026-10-03T00:00:00Z")
        approved = prepare_monitoring(thesis, store, approve=True, now="2026-10-03T00:00:00Z")
        self.assertEqual(approved.status, "monitoring")
        # Approval is durable; a restart can continue read-only monitoring without re-approval.
        resumed = prepare_monitoring(thesis, store, approve=False, now="2026-10-03T00:01:00Z")
        self.assertEqual(resumed.status, "monitoring")

    def test_synthetic_regression_remains_supported_then_invalidated(self) -> None:
        snapshot = Path(__file__).parents[1] / "examples" / "thesis_replay.json"
        thesis, events, _ = load_snapshot(snapshot)
        first = replay(thesis, events)
        second = replay(thesis, events)
        self.assertEqual([item.status for item in first], ["supported", "invalidated"])
        self.assertEqual([item.output_hash for item in first], [item.output_hash for item in second])

    def test_compiler_sanitizes_provider_quota_error(self) -> None:
        error = HTTPError("https://api.openai.com/v1/responses", 429, "limited", {},
                          BytesIO(b'{"error":{"code":"insufficient_quota","message":"secret detail"}}'))
        compiler = ThesisCompiler(api_key="test-secret", model="test-model")
        with patch("flow_thesis_ledger.ai.urlopen", side_effect=error):
            with self.assertRaises(ThesisCompileError) as raised:
                compiler.compile("AAPL total premium above 1000")
        self.assertEqual(raised.exception.category, "insufficient_quota")
        self.assertEqual(raised.exception.status, 429)
        self.assertNotIn("secret detail", str(raised.exception))
        self.assertNotIn("test-secret", str(raised.exception))

    def test_safe_shape_reports_field_names_and_types_without_values(self) -> None:
        shape = _safe_shape({"id": "private-id", "ticker_symbol": "AAPL", "total_premium": 12345})
        self.assertEqual(shape, {"type": "object", "fields": {
            "id": "string", "ticker_symbol": "string", "total_premium": "number",
        }})
        self.assertNotIn("private-id", repr(shape))
        self.assertNotIn("AAPL", repr(shape))

    def test_entitlement_check_reports_only_safe_shapes(self) -> None:
        class Client:
            def flow_alerts(self, params):
                return UWResponse(200, {}, {"data": [{"id": "private-id", "ticker_symbol": "AAPL", "created_at": "2026-10-03T10:00:00Z"}]})
            def flow_alert(self, alert_id):
                return UWResponse(200, {}, {"alert": {"id": alert_id, "ticker_symbol": "AAPL"}, "has_more": False, "trades": [{"price": 1.5}]})
        report = check(Client())
        safe = repr(report)
        self.assertEqual([item["status"] for item in report], [200, 200])
        self.assertNotIn("private-id", safe)
        self.assertNotIn("AAPL", safe)
        self.assertNotIn("1.5", safe)


if __name__ == "__main__":
    unittest.main()

"""Safe, read-only endpoint and entitlement check. Never prints response content or secrets."""

from __future__ import annotations

import json

from .uw_api import UWAPIError, UWClient
from .uw_ingest import classify_uw_error


def _kind(value: object) -> str:
    if value is None: return "null"
    if isinstance(value, bool): return "boolean"
    if isinstance(value, (int, float)): return "number"
    if isinstance(value, str): return "string"
    if isinstance(value, list): return "array"
    if isinstance(value, dict): return "object"
    return "other"


def _safe_shape(value: object) -> dict[str, object]:
    """Describe keys and JSON types only; never return field values."""
    if not isinstance(value, dict):
        return {"type": _kind(value)}
    return {"type": "object", "fields": {str(key): _kind(item) for key, item in sorted(value.items())}}


def check(client: UWClient) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    try:
        response = client.flow_alerts({"limit": 1, "all_opening": "false"})
        body = response.body
        results.append({
            "endpoint": "GET /api/option-trades/flow-alerts",
            "status": response.status,
            "access": "available" if response.status == 200 else "inconclusive",
            "response_contract": "data array" if isinstance(body, dict) and isinstance(body.get("data"), list) else "unexpected shape",
            "rows_returned": len(body["data"]) if isinstance(body, dict) and isinstance(body.get("data"), list) else None,
            "first_row_shape": _safe_shape(body["data"][0]) if isinstance(body, dict) and body.get("data") else None,
        })
        rows = body.get("data", []) if isinstance(body, dict) else []
        if rows and isinstance(rows[0], dict) and (rows[0].get("id") or rows[0].get("alert_id")):
            alert_id = str(rows[0].get("id") or rows[0].get("alert_id"))
            try:
                detail = client.flow_alert(alert_id)
                detail_body = detail.body
                results.append({
                    "endpoint": "GET /api/option-trades/flow-alerts/{id}",
                    "status": detail.status,
                    "access": "available" if detail.status == 200 else "inconclusive",
                    "response_contract": "alert/trades object" if isinstance(detail_body, dict) else "unexpected shape",
                    "top_level_fields": sorted(str(key) for key in detail_body) if isinstance(detail_body, dict) else [],
                    "alert_shape": _safe_shape(detail_body.get("alert")) if isinstance(detail_body, dict) and "alert" in detail_body else None,
                    "first_trade_shape": _safe_shape(detail_body["trades"][0]) if isinstance(detail_body, dict) and isinstance(detail_body.get("trades"), list) and detail_body["trades"] else None,
                })
            except UWAPIError as error:
                results.append({"endpoint": "GET /api/option-trades/flow-alerts/{id}", "status": error.status,
                                "access": classify_uw_error(error)})
        else:
            results.append({"endpoint": "GET /api/option-trades/flow-alerts/{id}", "status": None,
                            "access": "not tested: no alert id returned by list request"})
    except UWAPIError as error:
        results.append({"endpoint": "GET /api/option-trades/flow-alerts", "status": error.status,
                        "access": classify_uw_error(error)})
    return results


def main() -> None:
    try:
        client = UWClient(timeout=20, retries=1)
    except UWAPIError as error:
        raise SystemExit(str(error)) from None
    print("UW live check (read-only). Authorization: Bearer token; key value is not displayed.")
    for result in check(client):
        print(json.dumps(result, sort_keys=True))
    print("Entitlement conclusion applies only to the endpoints shown; this is not a full account-capability audit.")


if __name__ == "__main__":
    main()

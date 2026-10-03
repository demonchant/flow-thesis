"""Minimal read-only UW REST adapter. Contract fields must be checked against current OpenAPI."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://api.unusualwhales.com"


class UWAPIError(RuntimeError):
    def __init__(self, message: str, *, status: int | None = None, retryable: bool = False) -> None:
        super().__init__(message)
        self.status = status
        self.retryable = retryable


@dataclass(frozen=True)
class UWResponse:
    status: int
    headers: dict[str, str]
    body: Any


class UWClient:
    """Read-only REST client. Secrets are read from the process environment and never logged."""

    def __init__(self, api_key: str | None = None, *, timeout: float = 20.0, retries: int = 2) -> None:
        self._api_key = api_key or os.environ.get("UW_API_KEY") or os.environ.get("UNUSUAL_WHALES_API_KEY")
        if not self._api_key:
            raise UWAPIError("Set UW_API_KEY in the environment before making a live request")
        self.timeout = timeout
        self.retries = max(0, retries)

    def get(self, path: str, params: dict[str, Any] | None = None) -> UWResponse:
        if not path.startswith("/api/") or ".." in path:
            raise ValueError("path must be a safe UW /api/ path")
        query = urlencode({key: value for key, value in (params or {}).items() if value is not None}, doseq=True)
        url = BASE_URL + path + ("?" + query if query else "")
        request = Request(url, headers={"Authorization": f"Bearer {self._api_key}", "Accept": "application/json"})
        for attempt in range(self.retries + 1):
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    body = json.loads(response.read().decode("utf-8"))
                    return UWResponse(response.status, {k.lower(): v for k, v in response.headers.items()}, body)
            except HTTPError as error:
                retryable = error.code == 429 or 500 <= error.code < 600
                if not retryable or attempt >= self.retries:
                    # Do not include response body or request headers: either could contain sensitive data.
                    raise UWAPIError(f"UW request failed with HTTP {error.code}", status=error.code, retryable=retryable) from None
                delay = min(8.0, float(error.headers.get("Retry-After", 2**attempt)))
                time.sleep(max(0.0, delay))
            except (URLError, TimeoutError, json.JSONDecodeError) as error:
                if attempt >= self.retries:
                    raise UWAPIError(f"UW request failed: {type(error).__name__}", retryable=True) from None
                time.sleep(min(8.0, 0.5 * (2**attempt)))
        raise UWAPIError("UW request exhausted retries", retryable=True)

    def flow_alerts(self, params: dict[str, Any] | None = None) -> UWResponse:
        """Call the documented route with an intentional opening-trade filter.

        UW's operation page currently documents an `all_opening` default of true while
        warning that repeated-hit alerts are rarely all opening. Requiring an explicit
        choice avoids silently biasing the event set until a live contract check is done.
        """
        if params is None or "all_opening" not in params:
            raise ValueError("pass all_opening explicitly; do not rely on UW's documented default")
        if "limit" in params:
            try:
                limit = int(params["limit"])
            except (TypeError, ValueError):
                raise ValueError("limit must be an integer from 1 to 200") from None
            if not 1 <= limit <= 200:
                raise ValueError("limit must be an integer from 1 to 200")
        return self.get("/api/option-trades/flow-alerts", params)

    def flow_alert(self, alert_id: str) -> UWResponse:
        if not alert_id or "/" in alert_id:
            raise ValueError("alert_id must be a single path component")
        return self.get(f"/api/option-trades/flow-alerts/{alert_id}")

"""List names and short descriptions from the official UW MCP server.

Requires UW_API_KEY in this process environment. Never prints the credential,
raw JSON-RPC payload, response headers, or tool arguments/schemas.
"""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


URL = "https://api.unusualwhales.com/api/mcp"
PROTOCOL_VERSION = "2025-03-26"


class SafeMCPError(RuntimeError):
    pass


def _post(key: str, body: dict, session_id: str | None = None) -> tuple[int, dict | None, str | None]:
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": PROTOCOL_VERSION,
    }
    if session_id:
        headers["MCP-Session-Id"] = session_id
    request = Request(URL, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        with urlopen(request, timeout=20) as response:
            status = response.status
            response_text = response.read().decode("utf-8", errors="replace")
            session = response.headers.get("MCP-Session-Id") or session_id
    except HTTPError as error:
        # HTTP status is safe to report; response content is intentionally ignored.
        raise SafeMCPError(f"MCP server returned HTTP {error.code}") from None
    except (URLError, TimeoutError):
        raise SafeMCPError("MCP server could not be reached") from None
    if not response_text.strip():
        return status, None, session
    if "text/event-stream" in response.headers.get("Content-Type", ""):
        messages = []
        for line in response_text.splitlines():
            if line.startswith("data:"):
                messages.append(line[5:].strip())
        response_text = next((line for line in reversed(messages) if line), "")
    try:
        parsed = json.loads(response_text) if response_text else None
    except json.JSONDecodeError:
        raise SafeMCPError("MCP server returned an unsupported response format") from None
    if parsed is not None and not isinstance(parsed, dict):
        raise SafeMCPError("MCP server returned an invalid JSON-RPC response")
    if parsed and parsed.get("error"):
        raise SafeMCPError("MCP server rejected the tools/list request")
    return status, parsed, session


def main() -> int:
    key = os.environ.get("UW_API_KEY")
    if not key:
        print("UW_API_KEY is not available to this process.", file=sys.stderr)
        return 2
    try:
        _, initialized, session = _post(key, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "uw-safe-tool-list", "version": "1.0.0"},
            },
        })
        if not initialized or not isinstance(initialized.get("result"), dict):
            raise SafeMCPError("MCP initialize handshake did not complete")
        _post(key, {"jsonrpc": "2.0", "method": "notifications/initialized"}, session)
        _, listed, _ = _post(key, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}, session)
        tools = listed.get("result", {}).get("tools", []) if listed else []
        if not isinstance(tools, list):
            raise SafeMCPError("MCP server returned an invalid tool catalog")
        print(f"Tool count: {len(tools)}")
        for tool in tools:
            if isinstance(tool, dict) and isinstance(tool.get("name"), str):
                name = tool["name"].replace("\n", " ")[:120]
                description = tool.get("description", "")
                if not isinstance(description, str):
                    description = ""
                description = " ".join(description.split())[:240]
                print(f"- {name}: {description}")
        return 0
    except SafeMCPError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

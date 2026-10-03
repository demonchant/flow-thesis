# Unusual Whales MCP plugin

This project includes an optional Codex plugin scaffold for the official hosted Unusual Whales MCP server. It contains no API key. Each user must have UW API access and expose their own `UW_API_KEY` to the Codex process.

The project Codex MCP entry is `../../.agents/plugins/marketplace.json`; it marks this plugin available for the project marketplace. The server URL and environment-variable reference are in `.mcp.json`. Codex loads MCP servers at startup, so restart/reload the Codex session after configuring the environment.

To query the exact tools exposed to your account, from a PowerShell window where `UW_API_KEY` is already available:

```powershell
python plugins/unusual-whales/scripts/list_tools.py
```

The script performs the MCP initialize handshake and `tools/list`, then prints names and short descriptions only. It never prints credentials, response headers, data results, or argument schemas. The official UW server documents 200+ market-data endpoints across stock, options, flow, dark pool, congress, insider, institutions, market, earnings, ETF, shorts, seasonality, screener, futures (premium), politicians (premium), and news categories. Your exact tool list is account/entitlement dependent; premium tools may not be available to every API key.

Official server repository and catalog: https://github.com/unusual-whales/unusual-whales-official-mcp

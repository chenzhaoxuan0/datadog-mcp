# datadog-mcp

A Datadog observability MCP server powered by [Dedalus](https://dedaluslabs.ai). All tools are read-only in v1.

## Tools

| Tool | Description | Read/Write |
|------|-------------|-----------|
| `list_monitors` | List Datadog monitors with optional name/tag filtering | Read |
| `get_monitor` | Get details for a specific monitor | Read |
| `list_dashboards` | List Datadog dashboards | Read |
| `get_dashboard` | Get full dashboard layout and widgets | Read |
| `query_metrics` | Query timeseries metrics over a time range | Read |
| `search_logs` | Search Datadog logs with query and time filters | Read |
| `list_incidents` | List incidents (default: active/stable/resolved) | Read |
| `list_slos` | List SLOs with optional query filter | Read |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DD_API_KEY` | Yes | Datadog API key |
| `DD_APP_KEY` | Yes | Datadog application key |
| `DD_SITE` | No | Datadog site (default: `datadoghq.com`) |
| `DEDALUS_API_KEY` | Yes | Dedalus platform API key |
| `DEDALUS_API_URL` | No | Dedalus API base URL |
| `DEDALUS_AS_URL` | No | Dedalus auth server URL (default: `https://as.dedaluslabs.ai`) |

### Supported DD_SITE values

`datadoghq.com`, `datadoghq.eu`, `ap1.datadoghq.com`, `ap2.datadoghq.com`, `us3.datadoghq.com`, `us5.datadoghq.com`, `ddog-gov.com`

## Auth Architecture

Datadog requires two headers (`DD-API-KEY` + `DD-APPLICATION-KEY`) on every request. The primary API key uses standard DAuth dispatch. The application key is attached in the centralized dispatch helper. Tool code never reads either key directly. See `docs/auth-architecture.md` for details.

## Quick Start

```bash
uv sync
cp .env.example .env
# Edit .env with your keys
uv run python src/main.py
```

## Testing

```bash
uv run pytest tests/test_tools.py tests/test_security.py -v

# Live tests (requires DD_API_KEY + DD_APP_KEY)
uv run pytest tests/test_connection_live.py -v
```

## Source Decision

**Build native (Python REST)**. No official Datadog MCP exists. Community implementations are TypeScript and not adaptable to DAuth.

## License

MIT

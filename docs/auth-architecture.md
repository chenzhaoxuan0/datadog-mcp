# Auth Architecture: Datadog MCP

## Challenge

Datadog requires two secret-backed headers on every API request:
- `DD-API-KEY: <api_key>`
- `DD-APPLICATION-KEY: <app_key>`

The `Connection` class supports a single `auth_header_name` + `auth_header_format` pair, so dual-secret headers cannot be expressed through DAuth dispatch alone.

## Decision

**Hybrid approach (ADR-001):**

1. Primary auth (`DD-API-KEY`) uses standard DAuth: `Connection(auth_header_name="DD-API-KEY", auth_header_format="{api_key}")` with `SecretKeys(api_key="DD_API_KEY")`.
2. Secondary auth (`DD-APPLICATION-KEY`) is attached in the centralized `_dispatch_datadog` helper via `HttpRequest.headers`, reading `DD_APP_KEY` from environment.

## Security properties

- Tool code never reads `DD_APP_KEY` directly.
- The dispatch helper is the single point of secret access.
- Neither key is logged, returned in errors, or exposed to tool result types.
- Error messages are sanitized to exclude header values.

## Rationale

This follows the same pattern as HuggingFace MCP ADR-001 (Gradio Space API) and kernel-mcp (SDK direct). The DAuth framework does not support multi-secret per-connection auth, so a documented transport-layer exception is required.

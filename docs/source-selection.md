# Source Selection: Datadog MCP

**Decision: Build native (Python REST)**

Evaluated `GeLi2001/datadog-mcp-server`:
- TypeScript-based, uses stdio transport
- Not easily adaptable to Type 3 DAuth pattern
- Limited tool surface, no tests
- Would require full rewrite of auth layer

No official Datadog MCP server exists. Datadog has not published MCP tooling.

Decision: Build natively using `dedalus-mcp` against Datadog REST API v1/v2.

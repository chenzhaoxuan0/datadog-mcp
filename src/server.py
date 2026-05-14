from __future__ import annotations

import os

from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings

from datadog import (
    datadog_conn,
    get_dashboard,
    get_monitor,
    list_dashboards,
    list_incidents,
    list_monitors,
    list_slos,
    query_metrics,
    search_logs,
)


def create_server() -> MCPServer:
    as_url = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
    return MCPServer(
        name="datadog-mcp",
        connections=[datadog_conn],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        authorization_server=as_url,
    )


async def main() -> None:
    server = create_server()
    server.collect(
        list_monitors,
        get_monitor,
        list_dashboards,
        get_dashboard,
        query_metrics,
        search_logs,
        list_incidents,
        list_slos,
    )
    await server.serve(port=8080)

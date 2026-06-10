from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlencode

from dedalus_mcp import HttpMethod, HttpRequest, get_context, tool
from dedalus_mcp.auth import Connection, SecretKeys
from dedalus_mcp.types import ToolAnnotations

from datadog.types import (
    DashboardSummary,
    GetDashboardResult,
    GetMonitorResult,
    IncidentSummary,
    ListDashboardsResult,
    ListIncidentsResult,
    ListMonitorsResult,
    ListSLOsResult,
    LogEntry,
    MetricQueryResult,
    MonitorSummary,
    SearchLogsResult,
    SLOSummary,
)

_CONN_NAME = os.getenv("MCP_SERVER_SLUG", "Zx/datadog-mcp").replace("/", "-")

_SITE_MAP = {
    "datadoghq.com": "https://api.datadoghq.com",
    "datadoghq.eu": "https://api.datadoghq.eu",
    "ap1.datadoghq.com": "https://api.ap1.datadoghq.com",
    "ap2.datadoghq.com": "https://api.ap2.datadoghq.com",
    "us3.datadoghq.com": "https://api.us3.datadoghq.com",
    "us5.datadoghq.com": "https://api.us5.datadoghq.com",
    "ddog-gov.com": "https://api.ddog-gov.com",
}


def _base_url() -> str:
    site = os.getenv("DD_SITE", "datadoghq.com")
    return _SITE_MAP.get(site, f"https://api.{site}")


def _get_app_key() -> str:
    return os.getenv("DD_APP_KEY", "")


datadog_conn = Connection(
    name=_CONN_NAME,
    secrets=SecretKeys(api_key="DD_API_KEY"),
    base_url=_base_url(),
    auth_header_name="DD-API-KEY",
    auth_header_format="{api_key}",
)


async def _dispatch(
    path: str,
    *,
    method: HttpMethod = HttpMethod.GET,
    body: dict | None = None,
    query: dict | None = None,
) -> tuple[Any, str | None]:
    if query:
        qs = urlencode({k: v for k, v in query.items() if v is not None})
        if qs:
            path = f"{path}?{qs}"

    headers: dict[str, str] = {
        "Accept": "application/json",
    }
    app_key = _get_app_key()
    if app_key:
        headers["DD-APPLICATION-KEY"] = app_key

    ctx = get_context()
    req = HttpRequest(method=method, path=path, body=body, headers=headers)
    resp = await ctx.dispatch(_CONN_NAME, req)
    if resp.success and resp.response is not None:
        raw = resp.response.body
        if resp.response.status >= 400:
            return {}, f"Datadog API error ({resp.response.status}): {raw}"
        return raw if raw is not None else {}, None
    return {}, resp.error.message if resp.error else "Datadog request failed"


# --- Tools ---


@tool(
    description="List Datadog monitors with optional filtering",
    tags=["datadog", "monitors", "list"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_monitors(
    name: str = "",
    tags: list[str] | None = None,
    limit: int = 50,
) -> ListMonitorsResult:
    query: dict[str, Any] = {"limit": min(max(limit, 1), 100)}
    if name:
        query["name"] = name
    if tags:
        query["tags"] = ",".join(tags)

    body, err = await _dispatch("/api/v1/monitor", query=query)
    if err:
        return ListMonitorsResult(success=False, error=err)

    monitors = body if isinstance(body, list) else body.get("monitors", [])
    return ListMonitorsResult(
        success=True,
        monitors=[MonitorSummary.from_api(m) for m in monitors],
    )


@tool(
    description="Get details for a specific Datadog monitor",
    tags=["datadog", "monitors", "read"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_monitor(monitor_id: int) -> GetMonitorResult:
    body, err = await _dispatch(f"/api/v1/monitor/{monitor_id}")
    if err:
        return GetMonitorResult(success=False, error=err)
    return GetMonitorResult(success=True, monitor=MonitorSummary.from_api(body))


@tool(
    description="List Datadog dashboards",
    tags=["datadog", "dashboards", "list"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_dashboards(limit: int = 50) -> ListDashboardsResult:
    body, err = await _dispatch("/api/v1/dashboard")
    if err:
        return ListDashboardsResult(success=False, error=err)

    dashboards = body.get("dashboards", []) if isinstance(body, dict) else body if isinstance(body, list) else []
    return ListDashboardsResult(
        success=True,
        dashboards=[DashboardSummary.from_api(d) for d in dashboards[:limit]],
    )


@tool(
    description="Get details for a specific Datadog dashboard",
    tags=["datadog", "dashboards", "read"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_dashboard(dashboard_id: str) -> GetDashboardResult:
    body, err = await _dispatch(f"/api/v1/dashboard/{dashboard_id}")
    if err:
        return GetDashboardResult(success=False, error=err)
    return GetDashboardResult(success=True, dashboard=body)


@tool(
    description="Query Datadog metrics over a time range",
    tags=["datadog", "metrics", "query"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def query_metrics(query: str, start: int, end: int) -> MetricQueryResult:
    if not query.strip():
        return MetricQueryResult(success=False, error="Query must not be empty")

    body, err = await _dispatch(
        "/api/v1/query",
        query={"query": query, "from": str(start), "to": str(end)},
    )
    if err:
        return MetricQueryResult(success=False, error=err)

    series = body.get("series", []) if isinstance(body, dict) else []
    return MetricQueryResult(
        success=True,
        series=series,
        from_ts=body.get("from_date", 0),
        to_ts=body.get("to_date", 0),
    )


@tool(
    description="Search Datadog logs",
    tags=["datadog", "logs", "search"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def search_logs(
    query: str,
    start: str = "",
    end: str = "",
    limit: int = 25,
) -> SearchLogsResult:
    limit = min(max(limit, 1), 100)
    filter_body: dict[str, Any] = {"query": query}
    if start:
        filter_body["from"] = start
    if end:
        filter_body["to"] = end

    payload = {
        "filter": filter_body,
        "page": {"limit": limit},
        "sort": "-timestamp",
    }

    body, err = await _dispatch("/api/v2/logs/events/search", method=HttpMethod.POST, body=payload)
    if err:
        return SearchLogsResult(success=False, error=err)

    log_data = body.get("data", []) if isinstance(body, dict) else []
    return SearchLogsResult(
        success=True,
        logs=[LogEntry.from_api(l) for l in log_data],
    )


@tool(
    description="List Datadog incidents",
    tags=["datadog", "incidents", "list"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_incidents(
    query: str = "state:(active OR stable OR resolved)",
    limit: int = 25,
) -> ListIncidentsResult:
    body, err = await _dispatch(
        "/api/v2/incidents/search",
        query={"query": query, "page[limit]": str(min(limit, 100))},
    )
    if err:
        return ListIncidentsResult(success=False, error=err)

    incidents = [i for i in (body.get("data", []) if isinstance(body, dict) else []) if isinstance(i, dict)]
    return ListIncidentsResult(
        success=True,
        incidents=[IncidentSummary.from_api(i) for i in incidents],
    )


@tool(
    description="List Datadog SLOs",
    tags=["datadog", "slos", "list"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_slos(
    query: str = "",
    limit: int = 50,
) -> ListSLOsResult:
    params: dict[str, Any] = {"limit": str(min(limit, 100))}
    if query:
        params["query"] = query

    body, err = await _dispatch("/api/v1/slo", query=params)
    if err:
        return ListSLOsResult(success=False, error=err)

    slos = body.get("data", []) if isinstance(body, dict) else []
    return ListSLOsResult(
        success=True,
        slos=[SLOSummary.from_api(s) for s in slos],
    )

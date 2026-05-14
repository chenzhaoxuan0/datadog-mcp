"""End-to-end live tests for all Datadog MCP tools against real API.

Uses httpx directly with both DD-API-KEY and DD-APPLICATION-KEY headers.
"""

from __future__ import annotations

import os
import time
from unittest.mock import patch
from urllib.parse import urlencode

import httpx
import pytest
from dotenv import load_dotenv

load_dotenv()


def _needs_creds():
    return not (os.getenv("DD_API_KEY") and os.getenv("DD_APP_KEY"))


skip_no_creds = pytest.mark.skipif(
    _needs_creds(),
    reason="DD_API_KEY or DD_APP_KEY not set",
)


def _dd_base_url() -> str:
    site = os.getenv("DD_SITE", "datadoghq.com")
    return f"https://api.{site}"


def _dd_headers() -> dict[str, str]:
    return {
        "DD-API-KEY": os.getenv("DD_API_KEY", ""),
        "DD-APPLICATION-KEY": os.getenv("DD_APP_KEY", ""),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _make_dispatch():
    """Create a _dispatch replacement that uses httpx with full auth."""
    base = _dd_base_url()
    headers = _dd_headers()

    async def _real_dispatch(path, *, method="GET", body=None, query=None):
        if query:
            qs = urlencode({k: v for k, v in query.items() if v is not None})
            if qs:
                path = f"{path}?{qs}"

        async with httpx.AsyncClient(base_url=base, headers=headers, timeout=30.0) as client:
            if method == "GET":
                resp = await client.get(path)
            elif method == "POST":
                resp = await client.post(path, json=body)
            else:
                resp = await client.request(method, path, json=body)

            if resp.status_code >= 400:
                return {}, f"HTTP {resp.status_code}: {resp.text[:200]}"

            try:
                return resp.json(), None
            except Exception:
                return {}, None

    return _real_dispatch


@pytest.mark.asyncio
@skip_no_creds
async def test_01_list_monitors():
    from datadog import list_monitors

    with patch("datadog.tools._dispatch", side_effect=_make_dispatch()):
        result = await list_monitors(limit=3)
    assert result.success, f"list_monitors failed: {result.error}"


@pytest.mark.asyncio
@skip_no_creds
async def test_02_get_monitor():
    from datadog import list_monitors, get_monitor

    with patch("datadog.tools._dispatch", side_effect=_make_dispatch()):
        list_result = await list_monitors(limit=1)
    if not list_result.success or not list_result.monitors:
        pytest.skip("No monitors available to test get_monitor")

    with patch("datadog.tools._dispatch", side_effect=_make_dispatch()):
        result = await get_monitor(monitor_id=list_result.monitors[0].id)
    assert result.success, f"get_monitor failed: {result.error}"


@pytest.mark.asyncio
@skip_no_creds
async def test_03_list_dashboards():
    from datadog import list_dashboards

    with patch("datadog.tools._dispatch", side_effect=_make_dispatch()):
        result = await list_dashboards(limit=3)
    assert result.success, f"list_dashboards failed: {result.error}"


@pytest.mark.asyncio
@skip_no_creds
async def test_04_query_metrics():
    from datadog import query_metrics

    now = int(time.time())
    with patch("datadog.tools._dispatch", side_effect=_make_dispatch()):
        result = await query_metrics(
            query="system.cpu.user{*}.rollup(avg, 60)",
            start=now - 3600,
            end=now,
        )
    assert result.success, f"query_metrics failed: {result.error}"


@pytest.mark.asyncio
@skip_no_creds
async def test_05_search_logs():
    from datadog import search_logs

    with patch("datadog.tools._dispatch", side_effect=_make_dispatch()):
        result = await search_logs(query="*", limit=3)
    if not result.success and ("indexes" in result.error.lower() or "400" in result.error):
        pytest.skip(f"Log indexes not configured: {result.error[:80]}")
    assert result.success, f"search_logs failed: {result.error}"


@pytest.mark.asyncio
@skip_no_creds
async def test_06_list_incidents():
    from datadog import list_incidents

    with patch("datadog.tools._dispatch", side_effect=_make_dispatch()):
        result = await list_incidents(limit=3)
    assert result.success, f"list_incidents failed: {result.error}"


@pytest.mark.asyncio
@skip_no_creds
async def test_07_list_slos():
    from datadog import list_slos

    with patch("datadog.tools._dispatch", side_effect=_make_dispatch()):
        result = await list_slos(limit=3)
    assert result.success, f"list_slos failed: {result.error}"


@pytest.mark.asyncio
@skip_no_creds
async def test_08_get_dashboard():
    from datadog import list_dashboards, get_dashboard

    with patch("datadog.tools._dispatch", side_effect=_make_dispatch()):
        list_result = await list_dashboards(limit=1)
    if not list_result.success or not list_result.dashboards:
        pytest.skip("No dashboards available to test get_dashboard")

    dash_id = list_result.dashboards[0].id
    with patch("datadog.tools._dispatch", side_effect=_make_dispatch()):
        result = await get_dashboard(dashboard_id=dash_id)
    assert result.success, f"get_dashboard failed: {result.error}"

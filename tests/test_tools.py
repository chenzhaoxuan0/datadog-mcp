from __future__ import annotations

from unittest.mock import patch

import pytest

from datadog import (
    get_dashboard,
    get_monitor,
    list_dashboards,
    list_incidents,
    list_monitors,
    list_slos,
    query_metrics,
    search_logs,
)
from datadog.types import (
    GetDashboardResult,
    GetMonitorResult,
    ListDashboardsResult,
    ListIncidentsResult,
    ListMonitorsResult,
    ListSLOsResult,
    MetricQueryResult,
    SearchLogsResult,
)


@pytest.fixture(autouse=True)
def _fake_dispatch():
    async def _noop(path, **kw):
        return {}, "not mocked"

    with patch("datadog.tools._dispatch", side_effect=_noop):
        yield


# --- list_monitors ---


@pytest.mark.asyncio
async def test_list_monitors_success():
    async def fake_dispatch(path, **kw):
        return [
            {"id": 1, "name": "CPU High", "type": "metric alert", "overall_state": "OK"},
            {"id": 2, "name": "Disk Full", "type": "metric alert", "overall_state": "Alert"},
        ], None

    with patch("datadog.tools._dispatch", side_effect=fake_dispatch):
        result = await list_monitors()

    assert isinstance(result, ListMonitorsResult)
    assert result.success
    assert len(result.monitors) == 2
    assert result.monitors[0].name == "CPU High"
    assert result.monitors[1].status == "Alert"


@pytest.mark.asyncio
async def test_list_monitors_error():
    async def fake_dispatch(path, **kw):
        return {}, "forbidden"

    with patch("datadog.tools._dispatch", side_effect=fake_dispatch):
        result = await list_monitors()

    assert not result.success


# --- get_monitor ---


@pytest.mark.asyncio
async def test_get_monitor():
    async def fake_dispatch(path, **kw):
        assert "/api/v1/monitor/123" in path
        return {"id": 123, "name": "Test Monitor", "type": "metric alert", "overall_state": "OK"}, None

    with patch("datadog.tools._dispatch", side_effect=fake_dispatch):
        result = await get_monitor(monitor_id=123)

    assert isinstance(result, GetMonitorResult)
    assert result.success
    assert result.monitor is not None
    assert result.monitor.id == 123


# --- list_dashboards ---


@pytest.mark.asyncio
async def test_list_dashboards():
    async def fake_dispatch(path, **kw):
        return {
            "dashboards": [
                {"id": "abc-123", "title": "Overview", "author": {"handle": "admin@co.com"}},
                {"id": "def-456", "title": "APM"},
            ]
        }, None

    with patch("datadog.tools._dispatch", side_effect=fake_dispatch):
        result = await list_dashboards()

    assert isinstance(result, ListDashboardsResult)
    assert result.success
    assert len(result.dashboards) == 2
    assert result.dashboards[0].title == "Overview"


# --- get_dashboard ---


@pytest.mark.asyncio
async def test_get_dashboard():
    async def fake_dispatch(path, **kw):
        assert "/api/v1/dashboard/abc-123" in path
        return {"id": "abc-123", "title": "Overview", "widgets": []}, None

    with patch("datadog.tools._dispatch", side_effect=fake_dispatch):
        result = await get_dashboard(dashboard_id="abc-123")

    assert isinstance(result, GetDashboardResult)
    assert result.success
    assert result.dashboard["title"] == "Overview"


# --- query_metrics ---


@pytest.mark.asyncio
async def test_query_metrics_success():
    async def fake_dispatch(path, **kw):
        return {
            "series": [{"metric": "system.cpu.user", "pointlist": [[1, 0.5]]}],
            "from_date": 1000,
            "to_date": 2000,
        }, None

    with patch("datadog.tools._dispatch", side_effect=fake_dispatch):
        result = await query_metrics(query="system.cpu.user{*}", start=1000, end=2000)

    assert isinstance(result, MetricQueryResult)
    assert result.success
    assert len(result.series) == 1
    assert result.from_ts == 1000


@pytest.mark.asyncio
async def test_query_metrics_empty_rejected():
    result = await query_metrics(query="  ", start=0, end=100)

    assert not result.success
    assert "empty" in result.error.lower()


# --- search_logs ---


@pytest.mark.asyncio
async def test_search_logs():
    async def fake_dispatch(path, **kw):
        return {
            "data": [
                {"attributes": {"timestamp": "2024-01-01T00:00:00Z", "message": "Error 500", "service": "api"}},
            ]
        }, None

    with patch("datadog.tools._dispatch", side_effect=fake_dispatch):
        result = await search_logs(query="service:api error")

    assert isinstance(result, SearchLogsResult)
    assert result.success
    assert len(result.logs) == 1
    assert result.logs[0].service == "api"


# --- list_incidents ---


@pytest.mark.asyncio
async def test_list_incidents():
    async def fake_dispatch(path, **kw):
        return {
            "data": [
                {"id": "inc-1", "attributes": {"title": "Outage", "state": "active", "severity": "SEV1"}},
            ]
        }, None

    with patch("datadog.tools._dispatch", side_effect=fake_dispatch):
        result = await list_incidents()

    assert isinstance(result, ListIncidentsResult)
    assert result.success
    assert result.incidents[0].title == "Outage"


# --- list_slos ---


@pytest.mark.asyncio
async def test_list_slos():
    async def fake_dispatch(path, **kw):
        return {
            "data": [
                {"id": "slo-1", "name": "API Availability", "target": 99.9},
            ]
        }, None

    with patch("datadog.tools._dispatch", side_effect=fake_dispatch):
        result = await list_slos()

    assert isinstance(result, ListSLOsResult)
    assert result.success
    assert result.slos[0].name == "API Availability"
    assert result.slos[0].target == 99.9

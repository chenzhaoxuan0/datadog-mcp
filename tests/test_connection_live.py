from __future__ import annotations

from http import HTTPStatus

import pytest
from dedalus_mcp.testing import ConnectionTester, HttpMethod
from dedalus_mcp.testing import TestRequest as Req


@pytest.mark.asyncio
async def test_list_dashboards_live(datadog_tester: ConnectionTester) -> None:
    """GET /api/v1/dashboard should return dashboards."""
    resp = await datadog_tester.request(
        Req(method=HttpMethod.GET, path="/api/v1/dashboard")
    )
    assert resp.success, f"List dashboards failed: status={resp.status} body={resp.body!r}"
    assert resp.status == HTTPStatus.OK

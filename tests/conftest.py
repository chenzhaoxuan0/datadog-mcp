from __future__ import annotations

import os

import pytest
from dedalus_mcp.testing import ConnectionTester
from dotenv import load_dotenv

from datadog import datadog_conn


@pytest.fixture(scope="session")
def datadog_tester() -> ConnectionTester:
    load_dotenv()
    if not os.getenv("DD_API_KEY") or not os.getenv("DD_APP_KEY"):
        pytest.skip("DD_API_KEY or DD_APP_KEY not set; skipping live tests")
    return ConnectionTester.from_env(datadog_conn)

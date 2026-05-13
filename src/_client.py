import asyncio
import os

from dotenv import load_dotenv
from dedalus_mcp.client import MCPClient

load_dotenv()


async def main() -> None:
    async with MCPClient("http://localhost:8080/mcp") as client:
        tools = await client.list_tools()
        print("Available tools:")
        for t in tools:
            print(f"  - {t.name}: {t.description[:80]}...")
        print()

        print("--- list_monitors ---")
        result = await client.call_tool("list_monitors", {"limit": 3})
        print(result)
        print()

        monitor_id = os.getenv("DATADOG_TEST_MONITOR_ID", "")
        if monitor_id:
            print("--- get_monitor ---")
            result = await client.call_tool("get_monitor", {"monitor_id": int(monitor_id)})
            print(result)
            print()

        print("--- list_dashboards ---")
        result = await client.call_tool("list_dashboards", {"limit": 3})
        print(result)
        print()

        dashboard_id = os.getenv("DATADOG_TEST_DASHBOARD_ID", "")
        if dashboard_id:
            print("--- get_dashboard ---")
            result = await client.call_tool("get_dashboard", {"dashboard_id": dashboard_id})
            print(result)
            print()

        metric_query = os.getenv("DATADOG_TEST_METRIC_QUERY", "system.cpu.user{*}")
        print("--- query_metrics ---")
        result = await client.call_tool("query_metrics", {
            "query": metric_query,
            "start": 1700000000,
            "end": 1700086400,
        })
        print(result)
        print()

        print("--- search_logs ---")
        result = await client.call_tool("search_logs", {"query": "service:web", "limit": 3})
        print(result)
        print()

        print("--- list_incidents ---")
        result = await client.call_tool("list_incidents", {"limit": 3})
        print(result)
        print()

        print("--- list_slos ---")
        result = await client.call_tool("list_slos", {"limit": 3})
        print(result)


if __name__ == "__main__":
    asyncio.run(main())

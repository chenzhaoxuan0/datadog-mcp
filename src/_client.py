import asyncio

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

        print("--- list_dashboards ---")
        result = await client.call_tool("list_dashboards", {"limit": 3})
        print(result)
        print()

        print("--- search_logs ---")
        result = await client.call_tool("search_logs", {"query": "service:web", "limit": 3})
        print(result)


if __name__ == "__main__":
    asyncio.run(main())

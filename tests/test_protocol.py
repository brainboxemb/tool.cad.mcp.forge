import asyncio
from fastmcp import Client
from forge_mcp.server import mcp

def test_discovery_and_call():
    async def run():
        async with Client(mcp) as client:
            tools = await client.list_tools()
            assert "environment" in {tool.name for tool in tools}
            result = await client.call_tool("environment", {})
            assert not result.is_error
            assert result.data["cad_ready"] is False
    asyncio.run(run())

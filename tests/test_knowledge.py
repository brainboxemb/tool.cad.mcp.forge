import asyncio
import os

from fastmcp import Client
import pytest

from forge_mcp.server import mcp


def test_unconfigured_knowledge(monkeypatch):
    monkeypatch.delenv("FORGE_SOURCE_ROOT", raising=False)
    async def run():
        async with Client(mcp) as client:
            with pytest.raises(Exception, match="FORGE_SOURCE_ROOT"):
                await client.call_tool("forge_api_lookup", {"name": "Box"})
    asyncio.run(run())


def test_real_forge_knowledge():
    if not os.environ.get("FORGE_SOURCE_ROOT"):
        pytest.fail("Real Forge checkout is required for CI acceptance")
    async def run():
        async with Client(mcp) as client:
            async def call(name, **args):
                result = await client.call_tool(name, args)
                assert not result.is_error
                assert result.data["forge_version"] == "0.19.0"
                return result.data
            box = await call("forge_api_lookup", name="Box")
            assert "length" in box["signature"]
            shape = await call("forge_api_lookup", name="Shape")
            assert "repeat_linear" in shape["members"]
            method = await call("forge_api_lookup", name="Shape.repeat_linear")
            assert method["signature"]
            assert (await call("forge_api_search", query="repeat_linear"))["matches"]
            assert (await call("forge_docs_search", query="placement"))["matches"]
            assert (await call("forge_examples_search", query="simple-box"))["matches"][0]["model"] == "simple-box"
            example = await call("forge_example_read", model="simple-box")
            assert "class SimpleBox" in example["source"]
            with pytest.raises(Exception, match="public"):
                await client.call_tool("forge_api_lookup", {"name": "Box.__class__"})
            with pytest.raises(Exception, match="model ID"):
                await client.call_tool("forge_example_read", {"model": "../secret"})
    asyncio.run(run())

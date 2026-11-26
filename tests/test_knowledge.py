import asyncio
import os
import json

from fastmcp import Client
import pytest

from forge_mcp.server import mcp


def test_skill_entrypoints_without_forge(monkeypatch):
    monkeypatch.delenv("FORGE_SOURCE_ROOT", raising=False)
    async def run():
        async with Client(mcp) as client:
            result = await client.call_tool("skill_list", {})
            assert {s["skill"] for s in result.data["skills"]} == {"forge-modeling", "solidcraft-to-forge"}
            for name in ("forge-modeling", "solidcraft-to-forge"):
                result = await client.call_tool("skill_reference", {"skill": name, "file": "SKILL.md"})
                assert result.data["content"].startswith("---")
            with pytest.raises(Exception, match="FORGE_SOURCE_ROOT"):
                await client.call_tool("skill_reference", {"skill": "forge-modeling", "file": "references/index.json"})
    asyncio.run(run())


def test_real_forge_skill_references():
    if not os.environ.get("FORGE_SOURCE_ROOT"):
        pytest.fail("Real Forge checkout is required for CI acceptance")
    async def run():
        async with Client(mcp) as client:
            async def read(file):
                result = await client.call_tool("skill_reference", {"skill": "forge-modeling", "file": file})
                assert not result.is_error
                assert result.data["forge_version"] == "0.19.0"
                return result.data["content"]
            index = json.loads(await read("references/index.json"))
            assert "references/examples/simple-box.py" in index["examples"]
            assert "Box" in index["api_symbols"]
            box = json.loads(await read("references/api/Box.json"))
            assert "length" in box["signature"]
            shape = json.loads(await read("references/api/Shape.json"))
            assert "rectangular_pattern" in shape["members"]
            method = json.loads(await read("references/api/Shape.rectangular_pattern.json"))
            assert method["signature"]
            assert "class SimpleBox" in await read("references/examples/simple-box.py")
            assert "Placement" in await read("references/api.md")
            assert await read("references/guide/getting-started.html")
            with pytest.raises(Exception, match="Unknown skill reference"):
                await read("../secret")
    asyncio.run(run())

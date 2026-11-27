import asyncio
import os
import json

from fastmcp import Client
import pytest

from forge_mcp import knowledge
from forge_mcp.server import mcp


def test_skill_entrypoints_without_forge(monkeypatch):
    monkeypatch.delenv("FORGE_SOURCE_ROOT", raising=False)
    async def run():
        async with Client(mcp) as client:
            result = await client.call_tool("skill_list", {})
            assert {s["skill"] for s in result.data["skills"]} == {
                "forge-modeling",
                "solidcraft-to-forge",
                "solidcraft-control",
            }
            for name in ("forge-modeling", "solidcraft-to-forge", "solidcraft-control"):
                result = await client.call_tool("skill_reference", {"skill": name, "file": "SKILL.md"})
                assert result.data["content"].startswith("---")
            modeling = await client.call_tool(
                "skill_reference", {"skill": "forge-modeling", "file": "SKILL.md"}
            )
            content = modeling.data["content"]
            assert "Starting a new `scpf/model.py`" in content
            assert "class Plate:" in content
            assert "from scpf import Anchor, Box" in content
            assert "def build(self):" in content
            assert "Plate()" in content
            assert "lower-case numeric class fields" in content
            assert "solidcraft-control" in content
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
                assert result.data["forge_version"] == "0.25.0"
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
            assert await read("references/cheatsheet.yml")
            assert await read("references/guide/getting-started.html")
            with pytest.raises(Exception, match="Unknown skill reference"):
                await read("../secret")
    asyncio.run(run())


def test_real_skill_references_do_not_run_git(monkeypatch):
    if not os.environ.get("FORGE_SOURCE_ROOT"):
        pytest.fail("Real Forge checkout is required for CI acceptance")
    monkeypatch.setattr(
        knowledge,
        "_git",
        lambda *args, **kwargs: pytest.fail("skill references must not run Git validation"),
    )

    async def run():
        async with Client(mcp) as client:
            first, second = await asyncio.gather(
                client.call_tool(
                    "skill_reference",
                    {"skill": "forge-modeling", "file": "references/index.json"},
                ),
                client.call_tool(
                    "skill_reference",
                    {"skill": "solidcraft-control", "file": "references/api.md"},
                ),
            )
            assert not first.is_error
            assert not second.is_error
            assert "documents" in first.data["content"]
            assert "Placement" in second.data["content"]

    asyncio.run(run())

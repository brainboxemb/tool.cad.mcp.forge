import asyncio
import os
import json

from fastmcp import Client
import pytest

from forge_mcp.server import mcp


SKILLS = {
    "forge-modeling",
    "forge-editing",
    "forge-checking",
    "forge-assemblies",
    "forge-sheetmetal",
    "solidcraft-to-forge",
}


def test_skill_entrypoints_and_local_references_without_forge(monkeypatch):
    monkeypatch.delenv("FORGE_SOURCE_ROOT", raising=False)

    async def run():
        async with Client(mcp) as client:
            tools = {tool.name for tool in await client.list_tools()}
            result = await client.call_tool("skill_list", {})
            skills = result.data["skills"]
            assert {item["skill"] for item in skills} == SKILLS
            for item in skills:
                assert set(item["tools"]) <= tools
                for file in ("SKILL.md", "reference.md"):
                    loaded = await client.call_tool(
                        "skill_reference",
                        {"skill": item["skill"], "file": file},
                    )
                    assert not loaded.is_error
                    assert loaded.data["content"].strip()
                if item["skill"] != "forge-checking":
                    skill = await client.call_tool(
                        "skill_reference",
                        {"skill": item["skill"], "file": "SKILL.md"},
                    )
                    assert "forge-checking" in skill.data["content"]
            with pytest.raises(Exception, match="FORGE_SOURCE_ROOT"):
                await client.call_tool(
                    "skill_reference",
                    {"skill": "forge-modeling", "file": "references/index.json"},
                )

    asyncio.run(run())


def test_real_forge_skill_references():
    if not os.environ.get("FORGE_SOURCE_ROOT"):
        pytest.fail("Real Forge checkout is required for CI acceptance")

    async def run():
        async with Client(mcp) as client:
            async def read(file, skill="forge-modeling"):
                result = await client.call_tool(
                    "skill_reference",
                    {"skill": skill, "file": file},
                )
                assert not result.is_error
                assert result.data["forge_version"] == "0.19.0"
                return result.data["content"]

            index = json.loads(await read("references/index.json"))
            assert "reference.md" in index["local_files"]
            assert "references/examples/simple-box.py" in index["examples"]
            assert "references/examples/revolute-joint.py" in index["examples"]
            assert "references/examples/sheet-fold.py" in index["examples"]
            assert "Box" in index["api_symbols"]

            box = json.loads(await read("references/api/Box.json"))
            assert "length" in box["signature"]
            shape = json.loads(await read("references/api/Shape.json"))
            assert "rectangular_pattern" in shape["members"]
            method = json.loads(await read("references/api/Shape.rectangular_pattern.json"))
            assert method["signature"]

            assert "class SimpleBox" in await read("references/examples/simple-box.py")
            assert "kind=\"revolute\"" in await read(
                "references/examples/revolute-joint.py",
                skill="forge-assemblies",
            )
            assert ".sheet_metal(" in await read(
                "references/examples/sheet-fold.py",
                skill="forge-sheetmetal",
            )
            assert "Placement" in await read("references/api.md")
            assert await read("references/guide/getting-started.html")

            with pytest.raises(Exception, match="Unknown skill reference"):
                await read("../secret")

    asyncio.run(run())

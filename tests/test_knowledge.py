import asyncio
import os
import json
import re

from fastmcp import Client
import pytest

from forge_mcp import knowledge, skills
from forge_mcp.server import mcp
from scpf import run_script


def test_skill_entrypoints_without_forge(monkeypatch):
    monkeypatch.delenv("FORGE_SOURCE_ROOT", raising=False)
    async def run():
        async with Client(mcp) as client:
            result = await client.call_tool("skill_list", {})
            assert {s["skill"] for s in result.data["skills"]} == {
                "forge-modeling",
                "forge-sheet-metal",
                "forge-plastics",
                "solidcraft-to-forge",
                "solidcraft-control",
            }
            for name in ("forge-modeling", "forge-sheet-metal", "forge-plastics", "solidcraft-to-forge", "solidcraft-control"):
                result = await client.call_tool("skill_reference", {"skill": name, "file": "SKILL.md"})
                assert result.data["content"].startswith("---")
            modeling = await client.call_tool(
                "skill_reference", {"skill": "forge-modeling", "file": "SKILL.md"}
            )
            content = modeling.data["content"]
            assert "Starting a new `scpf/model.py`" in content
            assert "class SpacerBlank:" in content
            assert "from scpf import Anchor, Cylinder" in content
            assert "def build(self):" in content
            assert "SpacerBlank()" in content
            assert "Lower-case numeric class fields" in content
            assert "Level 1" in content and "Level 2" in content and "Level 3" in content
            assert "Use this entrypoint alone" in content
            assert "not a prerequisite" in content
            assert "body + hole.on(body, face=Faces.TOP)" in content
            assert "forge-sheet-metal" in content and "forge-plastics" in content
            assert "If the task" in content and "skip it" in content
            assert "expected_sha256" in content
            assert "class Plate:" not in content
            assert "skill_reference" in content
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


def test_forge_modeling_file_contract_example_compiles(tmp_path):
    content = skills.skill_reference("forge-modeling", "SKILL.md")["content"]
    examples = re.findall(r"```python\n(.*?)```", content, flags=re.DOTALL)
    assert len(examples) == 1

    for index, source in enumerate(examples, start=1):
        path = tmp_path / f"skill-example-{index}.py"
        path.write_text(source, encoding="utf-8")
        document = run_script(path)
        commands = document["commands"]
        assert commands
        assert any(row["command"] == "parameters.add" for row in commands)


def test_specialized_skills_are_optional_and_control_is_not_authoring():
    for name in ("forge-sheet-metal", "forge-plastics"):
        skill = skills.skill_reference(name)["content"]
        assert "Use only when" in skill
        assert "forge-modeling" in skill
    control = skills.skill_reference("solidcraft-control")["content"]
    assert "No full SolidCraft command reference is required" in control
    assert "not a source" in control
    assert "0.49.0" in control and "0.50.0" in control


def test_specialized_references_resolve_against_pinned_forge():
    assert "sheet" in skills.skill_reference(
        "forge-sheet-metal", "references/guide/sheet-metal.html"
    )["content"].lower()
    for symbol in ("Lip", "SnapFit", "Boss", "Rest"):
        value = skills.skill_reference("forge-plastics", f"references/api/{symbol}.json")
        assert json.loads(value["content"])["signature"]
    for symbol in ("Sketch.sheet_metal", "Shape.fold", "Shape.flange",
                   "Shape.contour_flange", "Shape.hem", "Shape.path_flange", "Shape.perforate"):
        value = skills.skill_reference("forge-sheet-metal", f"references/api/{symbol}.json")
        assert json.loads(value["content"])["signature"]


@pytest.mark.parametrize("body, expected", [
    (
        "return Box(self.size, 18, 12).chamfer(1, edges=Edges.from_faces(Faces.TOP))",
        "solid.chamfer",
    ),
    (
        "body = Box(self.size, 24, 6, anchor=Anchor.BOTTOM)\n"
        "        hole = Hole(d=5, depth=Depth.THROUGH_ALL)\n"
        "        return body + hole.on(body, face=Faces.TOP)",
        "solid.extrude",
    ),
    (
        'with Sketch(plane="XY") as profile:\n'
        "            Rectangle2D(self.size, 17)\n"
        "        return profile.extrude(9)",
        "solid.extrude",
    ),
])
def test_forge_modeling_common_idioms_compile(tmp_path, body, expected):
    path = tmp_path / "idiom.py"
    source = (
        "from scpf import Anchor, Box, Depth, Edges, Faces, Hole, Rectangle2D, Sketch\n"
        "class Part:\n"
        "    size = 37.0\n"
        "    def build(self):\n"
        f"        {body}\n"
        "Part()\n"
    )
    path.write_text(source, encoding="utf-8")
    commands = run_script(path)["commands"]
    assert any(row["command"] == expected for row in commands)

import asyncio
import json
import os
import subprocess

from fastmcp import Client
import pytest

from forge_mcp import compiler, knowledge
from forge_mcp.server import mcp


MODEL = """class CompileBox:
    length = 20.0
    width = 10.0
    height = 5.0

    def build(self):
        return Box(self.length, self.width, self.height, anchor=Anchor.BOTTOM)

CompileBox()
"""


HOLE_MODEL = """class CompilePlate:
    length = 60.0
    width = 20.0
    thickness = 4.0
    hole_diameter = 8.0

    def build(self):
        plate = Box(
            self.length,
            self.width,
            self.thickness,
            anchor=Anchor.BOTTOM,
        )
        hole = Hole(d=self.hole_diameter, depth=Depth.THROUGH_ALL)
        return plate + hole.on(plate, face=Faces.TOP)

CompilePlate()
"""


def test_real_forge_compile_to_workspace_build(tmp_path, monkeypatch):
    if not os.environ.get("FORGE_SOURCE_ROOT"):
        pytest.fail("Real Forge checkout is required for compile acceptance")
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    compiler.set_execution_enabled(True)
    (tmp_path / "source").mkdir()
    (tmp_path / "source" / "model.py").write_text(MODEL, encoding="utf-8")

    async def run():
        async with Client(mcp) as client:
            result = await client.call_tool(
                "forge_compile",
                {"source_path": "source/model.py", "output_path": "build/solidcraft.json"},
            )
            assert not result.is_error
            assert result.data["ok"] is True
            assert result.data["forge_version"] == "0.25.0"
            assert result.data["commands"] > 0
            output = tmp_path / "build" / "solidcraft.json"
            assert output.is_file()
            assert len(json.loads(output.read_text())["commands"]) == result.data["commands"]

            read = await client.call_tool("workspace_read", {"path": "build/solidcraft.json"})
            assert read.data["sha256"] == result.data["sha256"]
    asyncio.run(run())


def test_real_forge_compile_plate_hole_to_workspace_build(tmp_path, monkeypatch):
    if not os.environ.get("FORGE_SOURCE_ROOT"):
        pytest.fail("Real Forge checkout is required for compile acceptance")
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    compiler.set_execution_enabled(True)
    (tmp_path / "source").mkdir()
    (tmp_path / "source" / "model.py").write_text(HOLE_MODEL, encoding="utf-8")

    async def run():
        async with Client(mcp) as client:
            result = await client.call_tool(
                "forge_compile",
                {"source_path": "source/model.py", "output_path": "build/hole.json"},
            )
            assert not result.is_error
            assert result.data["ok"] is True
            output = tmp_path / "build" / "hole.json"
            document = json.loads(output.read_text(encoding="utf-8"))
            assert len(document["commands"]) == result.data["commands"]
            assert result.data["commands"] > 0

    asyncio.run(run())


def test_compile_child_does_not_inherit_server_stdin(tmp_path, monkeypatch):
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    compiler.set_execution_enabled(True)
    monkeypatch.setattr(knowledge, "source_root", lambda: tmp_path)
    (tmp_path / "model.py").write_text(MODEL, encoding="utf-8")
    observed = {}

    def fake_run(command, **kwargs):
        observed.update(kwargs)
        output = tmp_path / "build" / "solidcraft.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps({
                "version": 2,
                "commands": [{"command": "document.create", "params": {}}],
            }),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(
            command, 0, stdout="compiled\n", stderr=""
        )

    monkeypatch.setattr(compiler.subprocess, "run", fake_run)
    result = compiler.compile_model("model.py")

    assert result["ok"] is True
    assert observed["stdin"] == subprocess.DEVNULL


def test_compile_does_not_run_git_validation(tmp_path, monkeypatch):
    if not os.environ.get("FORGE_SOURCE_ROOT"):
        pytest.fail("Real Forge checkout is required for compile acceptance")
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    compiler.set_execution_enabled(True)
    monkeypatch.setattr(
        knowledge,
        "_git",
        lambda *args, **kwargs: pytest.fail("forge_compile must not run Git validation"),
    )
    (tmp_path / "model.py").write_text(MODEL, encoding="utf-8")

    async def run():
        async with Client(mcp) as client:
            result = await client.call_tool("forge_compile", {"source_path": "model.py"})
            assert not result.is_error
            assert result.data["ok"] is True

    asyncio.run(run())


def test_compile_failure_is_structured_and_removes_stale_output(tmp_path, monkeypatch):
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    compiler.set_execution_enabled(True)
    (tmp_path / "bad.py").write_text("def broken(:\n", encoding="utf-8")
    (tmp_path / "build").mkdir()
    stale = tmp_path / "build" / "solidcraft.json"
    stale.write_text('{"commands":["stale"]}', encoding="utf-8")

    async def run():
        async with Client(mcp) as client:
            result = await client.call_tool("forge_compile", {"source_path": "bad.py"})
            assert not result.is_error
            assert result.data["ok"] is False
            assert result.data["error"] == "compile_failed"
            assert result.data["returncode"] != 0
            assert "SyntaxError" in result.data["stderr"]
            assert not stale.exists()
    asyncio.run(run())


def test_compile_restricts_output_source_and_transport(tmp_path, monkeypatch):
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    compiler.set_execution_enabled(True)
    (tmp_path / "model.py").write_text(MODEL, encoding="utf-8")
    (tmp_path / "native.sc").write_text("native", encoding="utf-8")

    async def run():
        async with Client(mcp) as client:
            with pytest.raises(Exception, match="below build"):
                await client.call_tool(
                    "forge_compile",
                    {"source_path": "model.py", "output_path": "commands.json"},
                )
            with pytest.raises(Exception, match="Python"):
                await client.call_tool("forge_compile", {"source_path": "native.sc"})
            compiler.set_execution_enabled(False)
            with pytest.raises(Exception, match="disabled"):
                await client.call_tool("forge_compile", {"source_path": "model.py"})
    try:
        asyncio.run(run())
    finally:
        compiler.set_execution_enabled(True)


def test_catalog_assembly_compile_can_import_read_only_component(tmp_path, monkeypatch):
    if not os.environ.get("FORGE_SOURCE_ROOT"):
        pytest.fail("Real Forge checkout is required for compile acceptance")

    library = tmp_path / "catalog"
    target = library / "models" / "assemblies" / "demo"
    dependency = library / "models" / "components" / "part"
    (target / "scpf").mkdir(parents=True)
    (dependency / "scpf").mkdir(parents=True)
    (target / "model.yml").write_text("title: Demo assembly\n", encoding="utf-8")
    (dependency / "model.yml").write_text("title: Part\n", encoding="utf-8")
    (dependency / "scpf" / "model.py").write_text(
        "VALUE = 12.0\n",
        encoding="utf-8",
    )
    (target / "scpf" / "model.py").write_text(
        "from scpf import Anchor, Box\n"
        "from models.components.part.scpf.model import VALUE\n\n"
        "class ImportedBox:\n"
        "    def build(self):\n"
        "        return Box(VALUE, 10.0, 5.0, anchor=Anchor.BOTTOM)\n\n"
        "ImportedBox()\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("CAD_LIBRARY_ROOT", str(library))
    monkeypatch.setenv("CAD_MODEL_ROOT", "models/assemblies/demo")
    monkeypatch.delenv("FORGE_WORKSPACE_ROOT", raising=False)
    compiler.set_execution_enabled(True)

    async def run():
        async with Client(mcp) as client:
            result = await client.call_tool(
                "forge_compile",
                {"source_path": "scpf/model.py", "output_path": "build/solidcraft.json"},
            )
            assert not result.is_error
            assert result.data["ok"] is True
            assert result.data["commands"] > 0
            assert (target / "build" / "solidcraft.json").is_file()

    asyncio.run(run())

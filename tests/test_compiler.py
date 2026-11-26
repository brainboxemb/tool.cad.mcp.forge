import asyncio
import json
import os

from fastmcp import Client
import pytest

from forge_mcp import compiler
from forge_mcp.server import mcp


MODEL = """class CompileBox:
    length = 20.0
    width = 10.0
    height = 5.0

    def build(self):
        return Box(self.length, self.width, self.height, anchor=Anchor.BOTTOM)

CompileBox()
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
            assert result.data["forge_version"] == "0.19.0"
            assert result.data["commands"] > 0
            output = tmp_path / "build" / "solidcraft.json"
            assert output.is_file()
            assert len(json.loads(output.read_text())["commands"]) == result.data["commands"]

            read = await client.call_tool("workspace_read", {"path": "build/solidcraft.json"})
            assert read.data["sha256"] == result.data["sha256"]
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


def test_catalog_target_can_compile_imported_component_owner(tmp_path, monkeypatch):
    if not os.environ.get("FORGE_SOURCE_ROOT"):
        pytest.fail("Real Forge checkout is required for compile acceptance")

    library = tmp_path / "catalog"
    component = library / "models" / "components" / "shared_block"
    target = library / "models" / "assemblies" / "sample_assembly"
    (component / "scpf").mkdir(parents=True)
    (target / "scpf").mkdir(parents=True)
    (component / "model.yml").write_text("title: Shared Block\n", encoding="utf-8")
    (target / "model.yml").write_text("title: Sample Assembly\n", encoding="utf-8")
    (component / "scpf" / "model.py").write_text(
        "from scpf import Anchor, Box, component\n"
        "@component\n"
        "class SharedBlock:\n"
        "    def build(self):\n"
        "        return Box(12, 8, 4, anchor=Anchor.BOTTOM)\n",
        encoding="utf-8",
    )
    (target / "scpf" / "model.py").write_text(
        "from models.components.shared_block.scpf.model import SharedBlock\n"
        "class SampleAssembly:\n"
        "    def build(self):\n"
        "        return SharedBlock()\n"
        "SampleAssembly()\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CAD_LIBRARY_ROOT", str(library))
    monkeypatch.setenv("CAD_MODEL_ROOT", "models/assemblies/sample_assembly")
    monkeypatch.delenv("FORGE_WORKSPACE_ROOT", raising=False)
    compiler.set_execution_enabled(True)

    async def run():
        async with Client(mcp) as client:
            dependency = await client.call_tool(
                "library_read_owner",
                {
                    "owner": "models/components/shared_block",
                    "path": "scpf/model.py",
                },
            )
            assert dependency.data["read_only"] is True
            assert "class SharedBlock" in dependency.data["content"]

            result = await client.call_tool(
                "forge_compile",
                {"source_path": "scpf/model.py", "output_path": "build/solidcraft.json"},
            )
            assert not result.is_error
            assert result.data["ok"] is True
            assert result.data["commands"] > 0

    asyncio.run(run())

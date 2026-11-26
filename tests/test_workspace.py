import asyncio
from pathlib import Path

from fastmcp import Client
import pytest

from forge_mcp import workspace
from forge_mcp.server import mcp


def test_workspace_roundtrip_and_native_inputs_are_read_only(tmp_path, monkeypatch):
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    workspace.set_write_enabled(True)
    (tmp_path / "original.sc").write_text("native design", encoding="utf-8")
    (tmp_path / "commands.json").write_text('{"commands":[]}', encoding="utf-8")
    (tmp_path / "source").mkdir()
    (tmp_path / "source" / "model.py").write_text("value = 1\n", encoding="utf-8")

    async def run():
        async with Client(mcp) as client:
            status = await client.call_tool("workspace_status", {})
            assert status.data["write_enabled"] is True
            listed = await client.call_tool("workspace_list", {"path": "."})
            paths = {row["path"] for row in listed.data["entries"]}
            assert {"original.sc", "commands.json", "source/model.py"} <= paths

            with pytest.raises(Exception, match="not text-readable"):
                await client.call_tool("workspace_read", {"path": "original.sc"})

            current = await client.call_tool("workspace_read", {"path": "source/model.py"})
            updated = await client.call_tool(
                "workspace_write",
                {
                    "path": "source/model.py",
                    "content": "value = 2\n",
                    "expected_sha256": current.data["sha256"],
                },
            )
            assert updated.data["created"] is False
            assert (tmp_path / "source" / "model.py").read_text() == "value = 2\n"

            created = await client.call_tool(
                "workspace_write", {"path": "source/new_model.py", "content": "value = 3\n"}
            )
            assert created.data["created"] is True

            with pytest.raises(Exception, match="Only Python"):
                await client.call_tool(
                    "workspace_write", {"path": "original.sc", "content": "changed"}
                )
            with pytest.raises(Exception, match="expected_sha256"):
                await client.call_tool(
                    "workspace_write", {"path": "source/model.py", "content": "stale\n"}
                )
            with pytest.raises(Exception, match="does not match"):
                await client.call_tool(
                    "workspace_write",
                    {"path": "source/model.py", "content": "stale\n", "expected_sha256": "0" * 64},
                )
    asyncio.run(run())


def test_workspace_blocks_escape_symlink_and_remote_write(tmp_path, monkeypatch):
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    outside = tmp_path.parent / "outside-model.py"
    outside.write_text("secret = 1\n", encoding="utf-8")
    link = tmp_path / "linked.py"
    try:
        link.symlink_to(outside)
    except OSError:
        link = None

    async def run():
        async with Client(mcp) as client:
            with pytest.raises(Exception, match="inside|escapes"):
                await client.call_tool("workspace_read", {"path": "../outside-model.py"})
            if link is not None:
                with pytest.raises(Exception, match="symlink"):
                    await client.call_tool("workspace_read", {"path": "linked.py"})
            workspace.set_write_enabled(False)
            with pytest.raises(Exception, match="disabled"):
                await client.call_tool(
                    "workspace_write", {"path": "source/model.py", "content": "x = 1\n"}
                )
    try:
        asyncio.run(run())
    finally:
        workspace.set_write_enabled(True)


def test_catalog_binding_limits_workspace_to_exact_model(tmp_path, monkeypatch):
    library = tmp_path / "catalog"
    selected = library / "models" / "selected"
    other = library / "models" / "other"
    selected.mkdir(parents=True)
    other.mkdir(parents=True)
    (selected / "model.yml").write_text("title: Selected\n", encoding="utf-8")
    (other / "model.yml").write_text("title: Other\n", encoding="utf-8")
    (selected / "model.py").write_text("selected = True\n", encoding="utf-8")
    (other / "model.py").write_text("other = True\n", encoding="utf-8")
    monkeypatch.setenv("CAD_LIBRARY_ROOT", str(library))
    monkeypatch.setenv("CAD_MODEL_ROOT", "models/selected")
    monkeypatch.delenv("FORGE_WORKSPACE_ROOT", raising=False)

    status = workspace.status()
    assert status["catalog_bound"] is True
    assert status["model_id"] == "selected"
    assert status["model_relative"] == "models/selected"
    assert workspace.read_file("model.py")["content"] == "selected = True\n"
    with pytest.raises(workspace.WorkspaceError):
        workspace.read_file("../other/model.py")


def test_catalog_dependencies_are_read_only_exact_owner_access(tmp_path, monkeypatch):
    library = tmp_path / "catalog"
    target = library / "models" / "assemblies" / "demo"
    dependency = library / "models" / "components" / "part"
    target.mkdir(parents=True)
    dependency_source = dependency / "scpf"
    dependency_source.mkdir(parents=True)
    (target / "model.yml").write_text("title: Demo assembly\n", encoding="utf-8")
    (dependency / "model.yml").write_text("title: Part\n", encoding="utf-8")
    (dependency_source / "model.py").write_text("VALUE = 12.0\n", encoding="utf-8")

    monkeypatch.setenv("CAD_LIBRARY_ROOT", str(library))
    monkeypatch.setenv("CAD_MODEL_ROOT", "models/assemblies/demo")
    monkeypatch.delenv("FORGE_WORKSPACE_ROOT", raising=False)

    listed = workspace.catalog_dependency_list("models/components/part")
    paths = {row["path"] for row in listed["entries"]}
    assert "models/components/part/model.yml" in paths
    assert "models/components/part/scpf/model.py" in paths
    assert listed["read_only"] is True

    source = workspace.catalog_dependency_read("models/components/part/scpf/model.py")
    assert source["owner"] == "models/components/part"
    assert source["content"] == "VALUE = 12.0\n"
    assert source["read_only"] is True

    with pytest.raises(workspace.WorkspaceError, match="exact model folder"):
        workspace.catalog_dependency_list("models/components")
    with pytest.raises(workspace.WorkspaceError, match="inside|escapes"):
        workspace.catalog_dependency_read("../outside.py")

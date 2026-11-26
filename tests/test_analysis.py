import asyncio
import json

from fastmcp import Client
import pytest

from forge_mcp.server import mcp


def test_input_summary_classifies_command_document_without_dumping_it(tmp_path, monkeypatch):
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    path = tmp_path / "existing.json"
    path.write_text(json.dumps({
        "commands": [
            {"command": "parameters.add", "params": {"name": "length", "expression": "20 mm"}},
            {"command": "parameters.add", "params": {"name": "width", "expression": "10 mm"}},
            {"command": "solid.box", "params": {
                "length": "length", "width": "width", "height": 5,
                "operation": "new", "body_name": "ExistingBox"
            }},
        ]
    }), encoding="utf-8")

    async def run():
        async with Client(mcp) as client:
            summary = await client.call_tool("model_input_summary", {"path": "existing.json"})
            assert summary.data["kind"] == "solidcraft_command_document"
            assert summary.data["command_count"] == 3
            assert summary.data["command_types"]["parameters.add"] == 2
            assert summary.data["parameter_names"] == ["length", "width"]
            assert summary.data["body_names"] == ["ExistingBox"]
            assert "content" not in summary.data
    asyncio.run(run())


def test_native_input_is_discoverable_but_not_raw_text_readable(tmp_path, monkeypatch):
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    native = tmp_path / "existing.sc"
    native.write_bytes(b"opaque-native-artifact")

    async def run():
        async with Client(mcp) as client:
            summary = await client.call_tool("model_input_summary", {"path": "existing.sc"})
            assert summary.data["kind"] == "solidcraft_native"
            assert summary.data["text_readable"] is False
            assert "solidcraft_analyze" in summary.data["inspect_with"]
            with pytest.raises(Exception, match="not text-readable"):
                await client.call_tool("workspace_read", {"path": "existing.sc"})
    asyncio.run(run())

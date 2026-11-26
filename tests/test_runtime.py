import asyncio
import base64
import os
from pathlib import Path
import shutil

from fastmcp import Client
from mcp.types import ImageContent
from PIL import Image
import io
import pytest

from forge_mcp import runtime
from forge_mcp.server import mcp


pytestmark = pytest.mark.skipif(
    os.environ.get("SOLIDCRAFT_RUNTIME_ACCEPTANCE") != "1",
    reason="real SolidCraft runtime acceptance runs in the released CAD runtime image",
)


def test_real_compile_replay_evaluate_and_snapshot(tmp_path, monkeypatch):
    fixture = os.environ.get("SOLIDCRAFT_TEST_COMMANDS")
    if not fixture:
        pytest.fail("SOLIDCRAFT_TEST_COMMANDS is required")
    fixture_path = Path(fixture)
    assert fixture_path.is_file()

    build = tmp_path / "build"
    build.mkdir()
    shutil.copy2(fixture_path, build / "solidcraft.json")
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    runtime.set_execution_enabled(True)

    async def run():
        async with Client(mcp) as client:
            replay = await client.call_tool("solidcraft_replay", {})
            assert not replay.is_error
            assert replay.data["ok"] is True
            assert replay.data["solidcraft_version"] == "0.49.0"
            native = tmp_path / replay.data["native"]
            assert native.is_file() and native.stat().st_size > 0

            evaluated = await client.call_tool(
                "solidcraft_evaluate",
                {"model_path": "build/model.sc", "include_full": True},
            )
            assert not evaluated.is_error
            assert evaluated.data["ok"] is True
            assert evaluated.data["summary"]["body_count"] == 1
            names = {row["name"] for row in evaluated.data["summary"]["parameters"]}
            assert {"length", "width", "height"} <= names
            assert evaluated.data["full_included"] is True

            components = await client.call_tool(
                "solidcraft_components",
                {"model_path": "build/model.sc", "compact": True, "bodies": True},
            )
            assert not components.is_error
            assert components.data["ok"] is True
            assert components.data["solidcraft_version"] == "0.49.0"
            assert components.data["result"] is not None
            assert (tmp_path / "build" / "components.json").is_file()

            rendered = await client.call_tool(
                "solidcraft_snapshot",
                {"model_path": "build/model.sc", "width": 480, "height": 360},
            )
            assert not rendered.is_error
            block = next(item for item in rendered.content if isinstance(item, ImageContent))
            png = base64.b64decode(block.data)
            with Image.open(io.BytesIO(png)) as image:
                assert image.format == "PNG"
                assert image.size == (480, 360)
                image.verify()
            assert (tmp_path / "build" / "model.png").is_file()

    asyncio.run(run())


def test_runtime_execution_can_be_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "model.sc").write_bytes(b"not-used")
    runtime.set_execution_enabled(False)

    async def run():
        async with Client(mcp) as client:
            with pytest.raises(Exception, match="disabled"):
                await client.call_tool(
                    "solidcraft_evaluate", {"model_path": "build/model.sc"}
                )
    try:
        asyncio.run(run())
    finally:
        runtime.set_execution_enabled(True)

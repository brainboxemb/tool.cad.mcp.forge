import asyncio
import base64
import io
import json
import os
from pathlib import Path
import shutil

from fastmcp import Client
from mcp.types import ImageContent
from PIL import Image, ImageChops
import pytest

from forge_mcp import runtime
from forge_mcp.server import mcp


pytestmark = pytest.mark.skipif(
    os.environ.get("SOLIDCRAFT_CONVERSION_ACCEPTANCE") != "1",
    reason="existing-design conversion acceptance runs in the released SolidCraft runtime",
)


def _parameter_map(summary):
    return {row["name"]: row["value"] for row in summary["parameters"]}


def _sole_body(summary):
    assert summary["body_count"] == 1
    assert len(summary["bodies"]) == 1
    return summary["bodies"][0]


def test_existing_native_design_can_be_understood_and_matched_by_forge(tmp_path, monkeypatch):
    original_commands = Path(os.environ["SOLIDCRAFT_ORIGINAL_COMMANDS"])
    translated_commands = Path(os.environ["SOLIDCRAFT_TRANSLATED_COMMANDS"])
    assert original_commands.is_file()
    assert translated_commands.is_file()

    original = tmp_path / "original"
    build = tmp_path / "build"
    original.mkdir()
    build.mkdir()
    shutil.copy2(original_commands, original / "existing-box.json")
    shutil.copy2(translated_commands, build / "translated.json")
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    runtime.set_execution_enabled(True)

    # Test setup creates the user's pre-existing native design independently of Forge.
    import subprocess
    subprocess.run(
        [
            "solidcraft-cli", "run", str(original / "existing-box.json"),
            "--save", str(original / "existing-box.sc"), "--quiet",
        ],
        check=True,
    )

    async def run():
        async with Client(mcp) as client:
            input_info = await client.call_tool(
                "model_input_summary", {"path": "original/existing-box.json"}
            )
            assert input_info.data["kind"] == "solidcraft_command_document"
            assert input_info.data["command_types"] == {
                "parameters.add": 3,
                "solid.box": 1,
            }

            original_analysis = await client.call_tool(
                "solidcraft_analyze",
                {
                    "model_path": "original/existing-box.sc",
                    "output_dir": "build/original-analysis",
                    "include_full_measurements": True,
                },
            )
            assert original_analysis.data["ok"] is True

            replay = await client.call_tool(
                "solidcraft_replay",
                {"commands_path": "build/translated.json", "native_path": "build/translated.sc"},
            )
            assert replay.data["ok"] is True

            translated_analysis = await client.call_tool(
                "solidcraft_analyze",
                {
                    "model_path": "build/translated.sc",
                    "output_dir": "build/translated-analysis",
                    "include_full_measurements": True,
                },
            )
            assert translated_analysis.data["ok"] is True

            expected = original_analysis.data["measurements"]
            actual = translated_analysis.data["measurements"]
            assert _parameter_map(expected) == _parameter_map(actual)

            eb = _sole_body(expected)
            ab = _sole_body(actual)
            assert eb["bbox"] == ab["bbox"]
            assert abs(eb["volume_mm3"] - ab["volume_mm3"]) < 1e-9
            assert eb["faces"] == ab["faces"]

            renders = []
            for model, output in (
                ("original/existing-box.sc", "build/original.png"),
                ("build/translated.sc", "build/translated.png"),
            ):
                result = await client.call_tool(
                    "solidcraft_snapshot",
                    {"model_path": model, "output_path": output, "width": 480, "height": 360},
                )
                block = next(item for item in result.content if isinstance(item, ImageContent))
                renders.append(Image.open(io.BytesIO(base64.b64decode(block.data))).convert("RGBA"))

            assert renders[0].size == renders[1].size == (480, 360)
            difference = ImageChops.difference(renders[0], renders[1])
            extrema = difference.getextrema()
            assert max(channel[1] for channel in extrema) <= 1

            skill = await client.call_tool(
                "skill_reference", {"skill": "solidcraft-to-forge", "file": "SKILL.md"}
            )
            text = skill.data["content"]
            for tool in (
                "model_input_summary",
                "solidcraft_analyze",
                "forge_compile",
                "solidcraft_replay",
                "solidcraft_snapshot",
            ):
                assert tool in text

    asyncio.run(run())

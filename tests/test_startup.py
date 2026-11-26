import asyncio
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

from fastmcp import Client
from fastmcp.client.transports import StdioTransport
import pytest


def _fake_solidcraft(tmp_path: Path, version: str = "0.49.0") -> Path:
    path = tmp_path / "solidcraft-test"
    path.write_text(
        "#!/usr/bin/env python3\n"
        f"print('SolidCraft {version}')\n",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def _forge_root() -> str:
    value = os.environ.get("FORGE_SOURCE_ROOT")
    if not value:
        pytest.fail("FORGE_SOURCE_ROOT is required for startup acceptance")
    return value


def _catalog(tmp_path: Path):
    library = tmp_path / "cad-library"
    model = library / "models" / "wall-hook"
    model.mkdir(parents=True)
    (model / "model.yml").write_text("title: Wall Hook\n", encoding="utf-8")
    return library, model


def test_doctor_accepts_explicit_catalog_and_model_root(tmp_path):
    cli = _fake_solidcraft(tmp_path)
    library, model = _catalog(tmp_path)
    result = subprocess.run(
        [
            sys.executable, "-m", "forge_mcp.server", "doctor",
            "--cad-library", str(library),
            "--model-root", "models/wall-hook",
            "--forge-source", _forge_root(),
            "--solidcraft-cli", str(cli),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["ready"] is True
    assert report["forge"]["version"] == "0.19.0"
    assert report["solidcraft"]["version"] == "0.49.0"
    assert report["workspace"]["root"] == str(model.resolve())
    assert report["workspace"]["cad_library_root"] == str(library.resolve())
    assert report["workspace"]["catalog_bound"] is True
    assert report["workspace"]["model_id"] == "wall-hook"
    assert report["workspace"]["model_relative"] == "models/wall-hook"


def test_doctor_rejects_wrong_solidcraft_version(tmp_path):
    cli = _fake_solidcraft(tmp_path, "0.48.1")
    library, _ = _catalog(tmp_path)
    result = subprocess.run(
        [
            sys.executable, "-m", "forge_mcp.server", "doctor",
            "--cad-library", str(library),
            "--model-root", "models/wall-hook",
            "--forge-source", _forge_root(),
            "--solidcraft-cli", str(cli),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["ready"] is False
    assert report["solidcraft"]["version"] == "0.48.1"


def test_doctor_rejects_model_outside_catalog(tmp_path):
    cli = _fake_solidcraft(tmp_path)
    library = tmp_path / "cad-library"
    library.mkdir()
    outside = tmp_path / "other-model"
    outside.mkdir()
    result = subprocess.run(
        [
            sys.executable, "-m", "forge_mcp.server", "doctor",
            "--cad-library", str(library),
            "--model-root", str(outside),
            "--forge-source", _forge_root(),
            "--solidcraft-cli", str(cli),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["ready"] is False
    assert "inside CAD_LIBRARY_ROOT" in report["workspace"]["error"]


def test_real_stdio_subprocess_uses_explicit_model_binding(tmp_path):
    cli = _fake_solidcraft(tmp_path)
    library, model = _catalog(tmp_path)
    transport = StdioTransport(
        command=sys.executable,
        args=[
            "-m", "forge_mcp.server",
            "--cad-library", str(library),
            "--model-root", "models/wall-hook",
            "--forge-source", _forge_root(),
            "--solidcraft-cli", str(cli),
        ],
    )

    async def run():
        async with Client(transport) as client:
            result = await client.call_tool("environment", {})
            assert not result.is_error
            assert result.data["cad_ready"] is True
            workspace = result.data["readiness"]["workspace"]
            assert workspace["catalog_bound"] is True
            assert workspace["model_id"] == "wall-hook"
            assert workspace["model_relative"] == "models/wall-hook"
            status = await client.call_tool("workspace_status", {})
            assert status.data["root"] == str(model.resolve())
            assert status.data["model_relative"] == "models/wall-hook"

    asyncio.run(run())

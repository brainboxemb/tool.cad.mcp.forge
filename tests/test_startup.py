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


def test_doctor_accepts_explicit_paths_without_running_cad(tmp_path):
    cli = _fake_solidcraft(tmp_path)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    result = subprocess.run(
        [
            sys.executable, "-m", "forge_mcp.server", "doctor",
            "--workspace", str(workspace),
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
    assert report["workspace"]["root"] == str(workspace.resolve())


def test_doctor_rejects_wrong_solidcraft_version(tmp_path):
    cli = _fake_solidcraft(tmp_path, "0.48.1")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    result = subprocess.run(
        [
            sys.executable, "-m", "forge_mcp.server", "doctor",
            "--workspace", str(workspace),
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


def test_real_stdio_subprocess_uses_explicit_client_arguments(tmp_path):
    cli = _fake_solidcraft(tmp_path)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    transport = StdioTransport(
        command=sys.executable,
        args=[
            "-m", "forge_mcp.server",
            "--workspace", str(workspace),
            "--forge-source", _forge_root(),
            "--solidcraft-cli", str(cli),
        ],
    )

    async def run():
        async with Client(transport) as client:
            result = await client.call_tool("environment", {})
            assert not result.is_error
            assert result.data["cad_ready"] is True
            assert result.data["readiness"]["solidcraft"]["version"] == "0.49.0"
            status = await client.call_tool("workspace_status", {})
            assert status.data["root"] == str(workspace.resolve())

    asyncio.run(run())

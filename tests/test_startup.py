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


def _fake_solidcraft(tmp_path: Path, version: str = "0.50.0") -> Path:
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
    model = library / "models" / "assemblies" / "sample-assembly"
    model.mkdir(parents=True)
    (model / "model.yml").write_text("title: Sample Assembly\n", encoding="utf-8")
    return library, model


def test_doctor_accepts_explicit_catalog_and_model_root(tmp_path):
    cli = _fake_solidcraft(tmp_path)
    library, model = _catalog(tmp_path)
    result = subprocess.run(
        [
            sys.executable, "-m", "forge_mcp.server", "doctor",
            "--cad-library", str(library),
            "--model-root", "models/assemblies/sample-assembly",
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
    assert report["forge"]["version"] == "0.25.0"
    assert report["solidcraft"]["version"] == "0.50.0"
    assert report["workspace"]["root"] == str(model.resolve())
    assert report["workspace"]["cad_library_root"] == str(library.resolve())
    assert report["workspace"]["catalog_bound"] is True
    assert report["workspace"]["model_id"] == "sample-assembly"
    assert report["workspace"]["model_relative"] == "models/assemblies/sample-assembly"


def test_doctor_rejects_owner_outside_models_even_with_model_yml(tmp_path):
    cli = _fake_solidcraft(tmp_path)
    library = tmp_path / "cad-library"
    wrong = library / "docs" / "fake-owner"
    wrong.mkdir(parents=True)
    (wrong / "model.yml").write_text("title: Wrong\n", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable, "-m", "forge_mcp.server", "doctor",
            "--cad-library", str(library),
            "--model-root", "docs/fake-owner",
            "--forge-source", _forge_root(),
            "--solidcraft-cli", str(cli),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "below CAD_LIBRARY_ROOT/models" in json.loads(result.stdout)["workspace"]["error"]


def test_workspace_argument_overrides_inherited_catalog_environment(tmp_path):
    cli = _fake_solidcraft(tmp_path)
    standalone = tmp_path / "standalone"
    standalone.mkdir()
    env = os.environ.copy()
    env["CAD_LIBRARY_ROOT"] = str(tmp_path / "missing-library")
    env["CAD_MODEL_ROOT"] = "models/components/missing"
    result = subprocess.run(
        [
            sys.executable, "-m", "forge_mcp.server", "doctor",
            "--workspace", str(standalone),
            "--forge-source", _forge_root(),
            "--solidcraft-cli", str(cli),
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["workspace"]["catalog_bound"] is False
    assert report["workspace"]["root"] == str(standalone.resolve())


def test_real_stdio_subprocess_reports_path_free_target_identity(tmp_path):
    cli = _fake_solidcraft(tmp_path)
    library, _ = _catalog(tmp_path)
    transport = StdioTransport(
        command=sys.executable,
        args=[
            "-m", "forge_mcp.server",
            "--cad-library", str(library),
            "--model-root", "models/assemblies/sample-assembly",
            "--forge-source", _forge_root(),
            "--solidcraft-cli", str(cli),
        ],
    )

    async def run():
        async with Client(transport) as client:
            result = await client.call_tool("environment", {})
            assert not result.is_error
            assert result.data["cad_ready"] is True
            assert result.data["readiness"]["solidcraft"]["configured"] is True
            readiness = result.data["readiness"]["workspace"]
            assert readiness["catalog_bound"] is True
            assert readiness["model_id"] == "sample-assembly"
            assert readiness["model_relative"] == "models/assemblies/sample-assembly"
            assert "root" not in readiness
            assert "cad_library_root" not in readiness

            status = await client.call_tool("workspace_status", {})
            assert status.data["model_relative"] == "models/assemblies/sample-assembly"
            assert "root" not in status.data
            assert "cad_library_root" not in status.data

    asyncio.run(run())


def test_environment_status_does_not_run_runtime_or_git_probes(monkeypatch, tmp_path):
    from forge_mcp import diagnostics, knowledge, runtime, workspace

    standalone = tmp_path / "standalone"
    standalone.mkdir()
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(standalone))
    monkeypatch.delenv("CAD_LIBRARY_ROOT", raising=False)
    monkeypatch.delenv("CAD_MODEL_ROOT", raising=False)
    monkeypatch.setattr(
        knowledge,
        "source_root",
        lambda: pytest.fail("environment must not validate Forge Git checkout"),
    )
    monkeypatch.setattr(
        runtime,
        "detect_version",
        lambda: pytest.fail("environment must not run solidcraft-cli --version"),
    )
    monkeypatch.setattr(
        diagnostics.metadata,
        "version",
        lambda name: {
            "fastmcp": "2.14.7",
            "scpf": "0.25.0",
        }[name],
    )
    runtime.set_cli_executable("solidcraft-cli")

    report = diagnostics.environment_status()

    assert report["configured"] is True
    assert report["forge"]["installed_version"] == "0.25.0"
    assert report["solidcraft"]["configured"] is True
    assert report["workspace"]["catalog_bound"] is False

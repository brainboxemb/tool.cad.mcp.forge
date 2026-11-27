"""Run the complete headless released SolidCraft stack acceptance."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[4]
MODEL_FIXTURE = ROOT / "modules" / "ci" / "fixtures" / "acceptance_box.py"


def _run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def _restore_environment(name: str, value: str | None) -> None:
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value


def _compile_fixture(workspace: Path, output_path: str) -> dict:
    from forge_mcp import compiler

    shutil.rmtree(workspace, ignore_errors=True)
    source = workspace / "source"
    source.mkdir(parents=True)
    shutil.copy2(MODEL_FIXTURE, source / "model.py")

    names = ("FORGE_WORKSPACE_ROOT", "CAD_LIBRARY_ROOT", "CAD_MODEL_ROOT")
    previous = {name: os.environ.get(name) for name in names}
    os.environ["FORGE_WORKSPACE_ROOT"] = str(workspace)
    os.environ.pop("CAD_LIBRARY_ROOT", None)
    os.environ.pop("CAD_MODEL_ROOT", None)
    try:
        result = compiler.compile_model("source/model.py", output_path)
    finally:
        for name, value in previous.items():
            _restore_environment(name, value)

    if not result["ok"]:
        raise RuntimeError(f"acceptance fixture compile failed: {result}")
    return result


def run() -> None:
    if not os.environ.get("FORGE_SOURCE_ROOT"):
        raise RuntimeError("FORGE_SOURCE_ROOT must point to the qualified Forge checkout")
    if not MODEL_FIXTURE.is_file():
        raise RuntimeError(f"missing acceptance model fixture: {MODEL_FIXTURE}")

    runtime = _compile_fixture(
        ROOT / "build" / "runtime-fixture",
        "build/solidcraft.json",
    )
    conversion = _compile_fixture(
        ROOT / "build" / "conversion-fixture",
        "build/translated.json",
    )
    print(
        f"prepared runtime={runtime['commands']} commands, "
        f"conversion={conversion['commands']} commands"
    )

    wheel_dir = ROOT / "build" / "runtime-wheel"
    shutil.rmtree(wheel_dir, ignore_errors=True)
    _run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            ".",
            "--no-deps",
            "-w",
            str(wheel_dir),
        ]
    )

    _run(
        [
            "docker",
            "run",
            "--rm",
            "-e",
            "SOLIDCRAFT_RUNTIME_ACCEPTANCE=1",
            "-e",
            "SOLIDCRAFT_CONVERSION_ACCEPTANCE=1",
            "-e",
            "SOLIDCRAFT_TEST_COMMANDS=/repo/build/runtime-fixture/build/solidcraft.json",
            "-e",
            "SOLIDCRAFT_ORIGINAL_COMMANDS=/repo/tests/fixtures/existing-box.json",
            "-e",
            "SOLIDCRAFT_TRANSLATED_COMMANDS=/repo/build/conversion-fixture/build/translated.json",
            "-v",
            f"{ROOT}:/repo:ro",
            "-w",
            "/repo",
            "ghcr.io/brainboxemb/cad-solidcraft:v0.3.8",
            "sh",
            "-c",
            (
                "python -m venv /tmp/mcp-venv && "
                "/tmp/mcp-venv/bin/pip install /repo/build/runtime-wheel/*.whl "
                "'pytest>=8,<9' 'Pillow>=10' && "
                "/tmp/mcp-venv/bin/python -m pytest -q -p no:cacheprovider "
                "tests/test_runtime.py tests/test_conversion.py"
            ),
        ]
    )

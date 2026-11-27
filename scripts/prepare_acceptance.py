"""Prepare both Forge-generated fixtures used by released-stack acceptance."""

from __future__ import annotations

import os
from pathlib import Path
import shutil

from forge_mcp import compiler


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MODEL_FIXTURE = REPOSITORY_ROOT / "tests" / "fixtures" / "acceptance_box.py"


def _restore_environment(name: str, value: str | None) -> None:
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value


def compile_fixture(workspace: Path, output_path: str) -> dict:
    shutil.rmtree(workspace, ignore_errors=True)
    source = workspace / "source"
    source.mkdir(parents=True)
    shutil.copy2(MODEL_FIXTURE, source / "model.py")

    previous = {
        name: os.environ.get(name)
        for name in ("FORGE_WORKSPACE_ROOT", "CAD_LIBRARY_ROOT", "CAD_MODEL_ROOT")
    }
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


def main() -> None:
    if not MODEL_FIXTURE.is_file():
        raise RuntimeError(f"missing acceptance model fixture: {MODEL_FIXTURE}")

    runtime = compile_fixture(
        REPOSITORY_ROOT / "build" / "runtime-fixture",
        "build/solidcraft.json",
    )
    conversion = compile_fixture(
        REPOSITORY_ROOT / "build" / "conversion-fixture",
        "build/translated.json",
    )
    print(
        f"prepared runtime={runtime['commands']} commands, "
        f"conversion={conversion['commands']} commands"
    )


if __name__ == "__main__":
    main()

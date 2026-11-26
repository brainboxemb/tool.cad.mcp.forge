"""Bounded Forge compilation for trusted local MCP sessions."""
from __future__ import annotations

import json
import subprocess
import sys

from . import knowledge, workspace

MAX_DIAGNOSTIC_CHARS = 8000
COMPILE_TIMEOUT_SECONDS = 30

_execution_enabled = True


class CompileError(ValueError):
    """Compile request violates the bounded Forge compilation contract."""


def set_execution_enabled(enabled: bool) -> None:
    """Enable Python model execution only for trusted local transport."""
    global _execution_enabled
    _execution_enabled = bool(enabled)


def _bounded(value: str | None) -> str:
    text = value or ""
    if len(text) <= MAX_DIAGNOSTIC_CHARS:
        return text
    return text[-MAX_DIAGNOSTIC_CHARS:]


def compile_model(source_path: str, output_path: str = "build/solidcraft.json") -> dict:
    """Compile one workspace Python model to SolidCraft command JSON."""
    if not _execution_enabled:
        raise CompileError("Forge compilation is disabled for this server transport")

    root, source = workspace._resolve(source_path, must_exist=True)
    if not source.is_file() or source.suffix.lower() != ".py":
        raise CompileError("forge_compile source must be an existing Python file")

    # Validate the installed package and its release-matched knowledge checkout.
    knowledge.source_root()

    _, output = workspace._resolve(output_path)
    relative_output = output.relative_to(root)
    if (
        not relative_output.parts
        or relative_output.parts[0] != "build"
        or output.suffix.lower() != ".json"
    ):
        raise CompileError("forge_compile output must be a .json file below build/")

    output.parent.mkdir(parents=True, exist_ok=True)
    workspace._reject_symlinks(root, relative_output.parent)
    if output.exists():
        if output.is_symlink() or not output.is_file():
            raise CompileError("forge_compile output target is not a regular file")
        output.unlink()

    command = [sys.executable, "-m", "scpf", str(source), "--out", str(output)]
    try:
        result = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=COMPILE_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        if output.exists():
            output.unlink()
        return {
            "ok": False,
            "source": source.relative_to(root).as_posix(),
            "output": relative_output.as_posix(),
            "returncode": None,
            "error": "timeout",
            "stdout": _bounded(exc.stdout if isinstance(exc.stdout, str) else ""),
            "stderr": _bounded(exc.stderr if isinstance(exc.stderr, str) else ""),
        }

    response = {
        "ok": result.returncode == 0,
        "source": source.relative_to(root).as_posix(),
        "output": relative_output.as_posix(),
        "returncode": result.returncode,
        "stdout": _bounded(result.stdout),
        "stderr": _bounded(result.stderr),
    }
    if result.returncode != 0:
        if output.exists():
            output.unlink()
        response["error"] = "compile_failed"
        return response

    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("SCPF reported success but produced no command JSON")

    try:
        document = json.loads(output.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("SCPF produced unreadable command JSON") from exc
    commands = document.get("commands") if isinstance(document, dict) else None
    if not isinstance(commands, list):
        raise RuntimeError("SCPF command JSON has no commands array")

    response.update(
        {
            "commands": len(commands),
            "bytes": output.stat().st_size,
            "sha256": workspace._file_sha(output),
            "forge_version": knowledge.FORGE_VERSION,
        }
    )
    return response

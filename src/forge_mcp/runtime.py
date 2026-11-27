"""Bounded SolidCraft CLI execution for trusted local MCP sessions."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping

from . import workspace

SOLIDCRAFT_VERSION = "0.50.0"
RUNTIME_TIMEOUT_SECONDS = 120
MAX_DIAGNOSTIC_CHARS = 8000
MAX_FULL_RESULT_BYTES = 200_000
MAX_RUNTIME_JSON_BYTES = 5_000_000
MAX_PNG_BYTES = 20_000_000
_VERSION = re.compile(r"(?<!\d)(\d+\.\d+\.\d+)(?!\d)")

_execution_enabled = True
_cli_executable = os.environ.get("SOLIDCRAFT_CLI", "solidcraft-cli")


class RuntimeError(ValueError):
    """SolidCraft runtime request violates the bounded execution contract."""


def set_execution_enabled(enabled: bool) -> None:
    """Enable SolidCraft execution only for trusted local transport."""
    global _execution_enabled
    _execution_enabled = bool(enabled)


def set_cli_executable(executable: str | None) -> None:
    """Select the SolidCraft CLI executable used by all bounded runtime calls."""
    global _cli_executable
    value = executable or os.environ.get("SOLIDCRAFT_CLI") or "solidcraft-cli"
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("SolidCraft CLI executable must be a non-empty path or command")
    _cli_executable = value.strip()


def cli_executable() -> str:
    """Return the configured SolidCraft CLI executable."""
    return _cli_executable


def _require_execution() -> None:
    if not _execution_enabled:
        raise RuntimeError("SolidCraft execution is disabled for this server transport")


def _bounded(value: str | None) -> str:
    text = value or ""
    return text if len(text) <= MAX_DIAGNOSTIC_CHARS else text[-MAX_DIAGNOSTIC_CHARS:]


def detect_version() -> str:
    """Return the configured SolidCraft CLI version without executing CAD."""
    try:
        result = subprocess.run(
            [_cli_executable, "--version"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("solidcraft-cli is unavailable") from exc
    text = (result.stdout or "") + " " + (result.stderr or "")
    match = _VERSION.search(text)
    if result.returncode != 0 or match is None:
        raise RuntimeError("Cannot determine SolidCraft runtime version")
    return match.group(1)


def _version() -> str:
    _require_execution()
    actual = detect_version()
    if actual != SOLIDCRAFT_VERSION:
        raise RuntimeError(
            f"SolidCraft runtime {actual} differs from required {SOLIDCRAFT_VERSION}"
        )
    return actual


def _build_output(path: str, suffix: str) -> tuple[Path, Path, Path]:
    root, output = workspace._resolve(path)
    relative = output.relative_to(root)
    if not relative.parts or relative.parts[0] != "build" or output.suffix.lower() != suffix:
        raise RuntimeError(f"Runtime output must be a {suffix} file below build/")
    output.parent.mkdir(parents=True, exist_ok=True)
    workspace._reject_symlinks(root, relative.parent)
    if output.exists():
        if output.is_symlink() or not output.is_file():
            raise RuntimeError("Runtime output target is not a regular file")
        output.unlink()
    return root, output, relative


def _run(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=RUNTIME_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("SolidCraft command timed out") from exc
    except OSError as exc:
        raise RuntimeError("solidcraft-cli is unavailable") from exc


def _result_failure(operation: str, result: subprocess.CompletedProcess) -> dict:
    return {
        "ok": False,
        "operation": operation,
        "returncode": result.returncode,
        "error": "solidcraft_failed",
        "stdout": _bounded(result.stdout),
        "stderr": _bounded(result.stderr),
    }


def replay(
    commands_path: str = "build/solidcraft.json",
    native_path: str = "build/model.sc",
) -> dict:
    """Replay generated command JSON into one native SolidCraft design."""
    version = _version()
    root, commands = workspace._resolve(commands_path, must_exist=True)
    relative_commands = commands.relative_to(root)
    if (
        not commands.is_file()
        or commands.suffix.lower() != ".json"
        or not relative_commands.parts
        or relative_commands.parts[0] != "build"
    ):
        raise RuntimeError("solidcraft_replay accepts generated JSON below build/ only")
    try:
        document = json.loads(commands.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Generated SolidCraft command JSON is unreadable") from exc
    if not isinstance(document, dict) or not isinstance(document.get("commands"), list):
        raise RuntimeError("Generated SolidCraft JSON has no commands array")

    _, native, relative_native = _build_output(native_path, ".sc")
    result = _run(
        [_cli_executable, "run", str(commands), "--save", str(native), "--quiet"],
        cwd=root,
    )
    if result.returncode != 0:
        if native.exists():
            native.unlink()
        return {
            **_result_failure("replay", result),
            "commands": relative_commands.as_posix(),
            "native": relative_native.as_posix(),
            "solidcraft_version": version,
        }
    if not native.is_file() or native.stat().st_size == 0:
        raise RuntimeError("SolidCraft replay reported success but produced no native model")
    return {
        "ok": True,
        "operation": "replay",
        "commands": relative_commands.as_posix(),
        "native": relative_native.as_posix(),
        "command_count": len(document["commands"]),
        "bytes": native.stat().st_size,
        "sha256": workspace._file_sha(native),
        "solidcraft_version": version,
        "stdout": _bounded(result.stdout),
        "stderr": _bounded(result.stderr),
    }


def _compact_rows(value: Any, fields: tuple[str, ...], limit: int = 100) -> list:
    if not isinstance(value, list):
        return []
    rows = []
    for item in value[:limit]:
        if isinstance(item, Mapping):
            rows.append({key: item[key] for key in fields if key in item})
        else:
            rows.append(item)
    return rows


def _summary(data: Mapping[str, Any]) -> dict:
    summary = {
        "available_sections": sorted(str(key) for key in data),
    }
    for key in ("body_count", "component_count", "occurrence_count"):
        if key in data:
            summary[key] = data[key]
    if "bodies" in data:
        summary["bodies"] = _compact_rows(
            data["bodies"],
            ("name", "bbox", "volume_mm3", "faces", "face_types", "center_of_mass", "sheet_metal", "closed"),
        )
    if "params" in data:
        summary["parameters"] = _compact_rows(data["params"], ("name", "value", "unit"), 200)
    if "timeline" in data:
        summary["timeline"] = _compact_rows(
            data["timeline"], ("type", "name", "error", "warning"), 200
        )
    if "sketches" in data:
        summary["sketches"] = _compact_rows(
            data["sketches"], ("name", "profiles", "curves", "dof", "status"), 100
        )
    if "components" in data:
        summary["components"] = _compact_rows(
            data["components"], ("name", "id", "grounded", "visible"), 100
        )
    if "occurrences" in data:
        summary["occurrences"] = _compact_rows(
            data["occurrences"], ("name", "component", "id", "grounded", "visible"), 200
        )
    return summary


def evaluate(
    model_path: str,
    output_path: str = "build/measurements.json",
    include_full: bool = False,
) -> dict:
    """Evaluate one native model and return compact structural/geometric evidence."""
    version = _version()
    root, model = workspace._resolve(model_path, must_exist=True)
    if not model.is_file() or model.suffix.lower() != ".sc":
        raise RuntimeError("solidcraft_evaluate requires an existing .sc model")
    _, output, relative_output = _build_output(output_path, ".json")
    result = _run(
        [_cli_executable, "eval", str(model), "--json-out", str(output)],
        cwd=root,
    )
    if result.returncode != 0:
        if output.exists():
            output.unlink()
        return {
            **_result_failure("evaluate", result),
            "model": model.relative_to(root).as_posix(),
            "output": relative_output.as_posix(),
            "solidcraft_version": version,
        }
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("SolidCraft eval reported success but produced no measurements")
    size = output.stat().st_size
    if size > MAX_RUNTIME_JSON_BYTES:
        raise RuntimeError("SolidCraft measurement JSON exceeds the runtime evidence limit")
    try:
        data = json.loads(output.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("SolidCraft produced unreadable measurement JSON") from exc
    if not isinstance(data, Mapping):
        raise RuntimeError("SolidCraft measurement result must be a JSON object")
    response = {
        "ok": True,
        "operation": "evaluate",
        "model": model.relative_to(root).as_posix(),
        "output": relative_output.as_posix(),
        "bytes": size,
        "sha256": workspace._file_sha(output),
        "solidcraft_version": version,
        "summary": _summary(data),
        "full_included": False,
        "stdout": _bounded(result.stdout),
        "stderr": _bounded(result.stderr),
    }
    if include_full and size <= MAX_FULL_RESULT_BYTES:
        response["measurements"] = dict(data)
        response["full_included"] = True
    return response



def components(
    model_path: str,
    output_path: str = "build/components.json",
    compact: bool = True,
    bodies: bool = False,
) -> dict:
    """Run the fixed read-only component.list inspection against one native model."""
    version = _version()
    root, model = workspace._resolve(model_path, must_exist=True)
    if not model.is_file() or model.suffix.lower() != ".sc":
        raise RuntimeError("solidcraft_components requires an existing .sc model")
    if not isinstance(compact, bool) or not isinstance(bodies, bool):
        raise RuntimeError("component inspection options must be booleans")

    _, output, relative_output = _build_output(output_path, ".json")
    script = output.with_name(".mcp-component-list.json")
    if script.exists():
        if script.is_symlink() or not script.is_file():
            raise RuntimeError("Component inspection command target is not a regular file")
        script.unlink()
    script.write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "command": "component.list",
                        "params": {"compact": compact, "bodies": bodies},
                    }
                ]
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    try:
        result = _run(
            [
                _cli_executable, "run", str(script),
                "--in", str(model),
                "--param-check", "strict",
                "--results",
                "--json-out", str(output),
                "--quiet",
            ],
            cwd=root,
        )
    finally:
        if script.exists():
            script.unlink()

    if result.returncode != 0:
        if output.exists():
            output.unlink()
        return {
            **_result_failure("components", result),
            "model": model.relative_to(root).as_posix(),
            "output": relative_output.as_posix(),
            "solidcraft_version": version,
        }
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("SolidCraft component inspection produced no result")
    if output.stat().st_size > MAX_RUNTIME_JSON_BYTES:
        raise RuntimeError("SolidCraft component result exceeds the runtime evidence limit")
    try:
        data = json.loads(output.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("SolidCraft produced unreadable component JSON") from exc
    return {
        "ok": True,
        "operation": "components",
        "model": model.relative_to(root).as_posix(),
        "output": relative_output.as_posix(),
        "bytes": output.stat().st_size,
        "sha256": workspace._file_sha(output),
        "solidcraft_version": version,
        "result": data,
        "stdout": _bounded(result.stdout),
        "stderr": _bounded(result.stderr),
    }


def snapshot(
    model_path: str,
    output_path: str = "build/model.png",
    width: int = 800,
    height: int = 600,
    camera: dict | None = None,
) -> bytes:
    """Render one deterministic SolidCraft PNG and return its bytes."""
    _version()
    root, model = workspace._resolve(model_path, must_exist=True)
    if not model.is_file() or model.suffix.lower() != ".sc":
        raise RuntimeError("solidcraft_snapshot requires an existing .sc model")
    for value, name in ((width, "width"), (height, "height")):
        if isinstance(value, bool) or not isinstance(value, int) or not 64 <= value <= 2048:
            raise RuntimeError(f"snapshot {name} must be an integer from 64 to 2048")
    _, output, _ = _build_output(output_path, ".png")
    command = [
        _cli_executable, "snapshot", str(model),
        "--out", str(output),
        "--width", str(width),
        "--height", str(height),
        "--no-grid", "--no-axes",
    ]
    if camera is not None:
        command.extend(["--camera", json.dumps(camera, separators=(",", ":"))])
    result = _run(command, cwd=root)
    if result.returncode != 0:
        if output.exists():
            output.unlink()
        raise RuntimeError(
            "SolidCraft snapshot failed: " + (_bounded(result.stderr) or _bounded(result.stdout))
        )
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("SolidCraft snapshot reported success but produced no PNG")
    if output.stat().st_size > MAX_PNG_BYTES:
        raise RuntimeError("SolidCraft PNG exceeds the image size limit")
    data = output.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("SolidCraft snapshot output is not a PNG")
    return data

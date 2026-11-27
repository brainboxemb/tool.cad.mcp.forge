"""Bounded control of the running SolidCraft GUI for trusted local MCP sessions."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import yaml
from scpf import live as scpf_live

from . import compiler, workspace


MAX_LIVE_RESULT_BYTES = 1_000_000
MAX_REPLAY_LOG_BYTES = 10_000_000
MAX_LOG_VALUE_BYTES = 32_000
PROJECT_FILE = "project.yml"

_execution_enabled = True


class LiveControlError(ValueError):
    """Live SolidCraft control violates the configured workbench contract."""


def set_execution_enabled(enabled: bool) -> None:
    global _execution_enabled
    _execution_enabled = bool(enabled)


def _require_execution() -> None:
    if not _execution_enabled:
        raise LiveControlError(
            "Live SolidCraft control is disabled for this server transport"
        )


def _project() -> dict:
    root = workspace._root()
    path = root / PROJECT_FILE
    defaults = {
        "schema": 1,
        "forge": {"source": "scpf/model.py"},
        "solidcraft": {"connect": "auto"},
        "evidence": {
            "enabled": True,
            "log": "build/session.jsonl",
            "render": "build/live/model.png",
        },
    }
    if not path.is_file():
        return defaults
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise LiveControlError(f"Cannot read {PROJECT_FILE}") from exc
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise LiveControlError(f"{PROJECT_FILE} must be a schema: 1 mapping")

    result = {
        "schema": 1,
        "forge": dict(defaults["forge"]),
        "solidcraft": dict(defaults["solidcraft"]),
        "evidence": dict(defaults["evidence"]),
    }
    for section in ("forge", "solidcraft", "evidence"):
        value = data.get(section)
        if value is not None:
            if not isinstance(value, dict):
                raise LiveControlError(
                    f"{PROJECT_FILE} section {section} must be a mapping"
                )
            result[section].update(value)

    source = result["forge"].get("source")
    if not isinstance(source, str) or not source.strip():
        raise LiveControlError("project forge.source must be a non-empty path")
    _relative_workspace_path(source, suffix=".py")

    connect = result["solidcraft"].get("connect", "auto")
    if not isinstance(connect, (str, int)) or isinstance(connect, bool):
        raise LiveControlError("project solidcraft.connect must be auto, port or address")

    enabled = result["evidence"].get("enabled", True)
    if not isinstance(enabled, bool):
        raise LiveControlError("project evidence.enabled must be boolean")
    for key, suffix in (("log", ".jsonl"), ("render", ".png")):
        value = result["evidence"].get(key)
        if not isinstance(value, str) or not value.strip():
            raise LiveControlError(f"project evidence.{key} must be a path")
        _build_path(value, suffix=suffix)
    return result


def _relative_workspace_path(value: str, *, suffix: str | None = None) -> Path:
    root, path = workspace._resolve(value)
    relative = path.relative_to(root)
    if suffix is not None and path.suffix.lower() != suffix:
        raise LiveControlError(f"Path must end in {suffix}")
    return relative


def _build_path(value: str, *, suffix: str) -> Path:
    relative = _relative_workspace_path(value, suffix=suffix)
    if not relative.parts or relative.parts[0] != "build":
        raise LiveControlError("Live evidence paths must stay below build/")
    return relative


def _connect() -> str | int:
    return _project()["solidcraft"].get("connect", "auto")


def _bounded_result(value: Any) -> Any:
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise LiveControlError("SolidCraft returned a non-JSON result") from exc
    if len(encoded.encode("utf-8")) > MAX_LIVE_RESULT_BYTES:
        raise LiveControlError(
            "SolidCraft live result exceeds the MCP result size limit"
        )
    return value


def _log_value(value: Any) -> Any:
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError):
        return {"summary": "non-json value omitted"}
    if len(encoded.encode("utf-8")) <= MAX_LOG_VALUE_BYTES:
        return value
    return {
        "summary": "value omitted from session log because it is too large",
        "bytes": len(encoded.encode("utf-8")),
    }


def _record(operation: str, *, inputs: dict, ok: bool, result: Any = None, error: str | None = None) -> None:
    project = _project()
    evidence = project["evidence"]
    if not evidence.get("enabled", True):
        return
    relative = _build_path(str(evidence["log"]), suffix=".jsonl")
    root, path = workspace._resolve(relative.as_posix())
    path.parent.mkdir(parents=True, exist_ok=True)
    workspace._reject_symlinks(root, path.relative_to(root).parent)
    row = {
        "time": datetime.now(timezone.utc).isoformat(),
        "operation": operation,
        "ok": bool(ok),
        "inputs": _log_value(inputs),
    }
    if result is not None:
        row["result"] = _log_value(result)
    if error is not None:
        row["error"] = str(error)[:8000]
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")


def project_status() -> dict:
    """Return bounded local workbench project settings without absolute paths."""
    project = _project()
    return {
        "project_file": PROJECT_FILE,
        "forge_source": project["forge"]["source"],
        "solidcraft_connect": project["solidcraft"]["connect"],
        "evidence": dict(project["evidence"]),
    }


def new_design(name: str | None = None) -> dict:
    """Create a new active SolidCraft GUI design through the authenticated control channel."""
    _require_execution()
    inputs = {"name": name}
    try:
        result = scpf_live.new_design(name=name, connect=_connect())
        result = _bounded_result(result)
    except Exception as exc:
        _record("solidcraft_live_new", inputs=inputs, ok=False, error=str(exc))
        raise LiveControlError(str(exc)) from exc
    _record("solidcraft_live_new", inputs=inputs, ok=True, result=result)
    return {"ok": True, **result}


def execute(command: str, params: dict | None = None) -> dict:
    """Execute one native SolidCraft engine command in the active GUI design."""
    _require_execution()
    if not isinstance(command, str) or not command.strip() or len(command) > 200:
        raise LiveControlError("command must be a non-empty SolidCraft command id")
    if params is None:
        params = {}
    if not isinstance(params, dict):
        raise LiveControlError("params must be a mapping")
    inputs = {"command": command, "params": params}
    try:
        batch = scpf_live.send_commands(
            [{"command": command, "params": params}],
            connect=_connect(),
        )
        batch = _bounded_result(batch)
    except Exception as exc:
        _record("solidcraft_live_execute", inputs=inputs, ok=False, error=str(exc))
        raise LiveControlError(str(exc)) from exc
    results = batch.get("results") if isinstance(batch, dict) else None
    native_result = (
        results[0]
        if isinstance(results, list) and len(results) == 1
        else results
    )
    response = {
        "ok": True,
        "command": command,
        "result": native_result,
        "completed": batch.get("completed") if isinstance(batch, dict) else None,
    }
    _record("solidcraft_live_execute", inputs=inputs, ok=True, result=response)
    return response


def inspect(
    measure: bool = False,
    sketch_counts: bool = False,
    timeline: bool | str = "summary",
    bodies: bool | str = "names",
) -> dict:
    """Inspect the active SolidCraft document through the native control protocol."""
    _require_execution()
    if not isinstance(measure, bool) or not isinstance(sketch_counts, bool):
        raise LiveControlError("inspect boolean options must be booleans")
    if timeline not in (True, False, "summary"):
        raise LiveControlError("timeline must be true, false or summary")
    if bodies not in (True, False, "names"):
        raise LiveControlError("bodies must be true, false or names")
    params = {
        "measure": measure,
        "sketch_counts": sketch_counts,
        "timeline": timeline,
        "bodies": bodies,
    }
    try:
        result = scpf_live._send_request(
            "document.inspect",
            params,
            connect=_connect(),
            timeout=120,
        )
        result = _bounded_result(result)
    except Exception as exc:
        _record("solidcraft_live_inspect", inputs=params, ok=False, error=str(exc))
        raise LiveControlError(str(exc)) from exc
    response = {"ok": True, "document": result}
    _record("solidcraft_live_inspect", inputs=params, ok=True, result=response)
    return response


def render(
    output_path: str | None = None,
    width: int = 960,
    height: int = 600,
    grid: bool = False,
    axes: bool = False,
) -> bytes:
    """Render the active SolidCraft GUI model using its current camera."""
    _require_execution()
    for value, name in ((width, "width"), (height, "height")):
        if isinstance(value, bool) or not isinstance(value, int) or not 64 <= value <= 2048:
            raise LiveControlError(f"{name} must be an integer from 64 to 2048")
    if not isinstance(grid, bool) or not isinstance(axes, bool):
        raise LiveControlError("grid and axes must be booleans")
    project = _project()
    target = output_path or str(project["evidence"]["render"])
    relative = _build_path(target, suffix=".png")
    root, path = workspace._resolve(relative.as_posix())
    path.parent.mkdir(parents=True, exist_ok=True)
    workspace._reject_symlinks(root, path.relative_to(root).parent)
    if path.exists():
        if path.is_symlink() or not path.is_file():
            raise LiveControlError("render output target is not a regular file")
        path.unlink()

    params = {
        "path": str(path),
        "width": width,
        "height": height,
        "grid": grid,
        "axes": axes,
    }
    try:
        result = scpf_live._send_request(
            "ui.render",
            params,
            connect=_connect(),
            timeout=120,
        )
        result = _bounded_result(result)
        if not path.is_file() or path.stat().st_size == 0:
            raise LiveControlError("SolidCraft ui.render produced no PNG")
        data = path.read_bytes()
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise LiveControlError("SolidCraft ui.render output is not a PNG")
    except Exception as exc:
        _record(
            "solidcraft_live_render",
            inputs={k: v for k, v in params.items() if k != "path"} | {
                "output": relative.as_posix()
            },
            ok=False,
            error=str(exc),
        )
        raise LiveControlError(str(exc)) from exc

    evidence = {
        "output": relative.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": workspace._file_sha(path),
        "solidcraft": result,
    }
    _record(
        "solidcraft_live_render",
        inputs={
            "output": relative.as_posix(),
            "width": width,
            "height": height,
            "grid": grid,
            "axes": axes,
        },
        ok=True,
        result=evidence,
    )
    return data


def forge_live(
    source_path: str | None = None,
    new: bool = True,
    design_name: str | None = None,
) -> dict:
    """Compile Forge source and apply its replay document to the running SolidCraft GUI."""
    _require_execution()
    if not isinstance(new, bool):
        raise LiveControlError("new must be boolean")
    project = _project()
    source = source_path or str(project["forge"]["source"])
    _relative_workspace_path(source, suffix=".py")
    commands_path = "build/live/solidcraft.json"
    inputs = {
        "source": source,
        "new": new,
        "design_name": design_name,
    }

    try:
        compiled = compiler.compile_model(source, commands_path)
        if not compiled.get("ok"):
            response = {"ok": False, "stage": "compile", "compile": compiled}
            _record("forge_live", inputs=inputs, ok=False, result=response)
            return response

        root, commands = workspace._resolve(commands_path, must_exist=True)
        document = json.loads(commands.read_text(encoding="utf-8"))
        fresh = None
        if new:
            fresh = scpf_live.new_design(
                name=design_name,
                connect=_connect(),
            )
        applied = scpf_live.send_document(document, connect=_connect())
        if not isinstance(applied, dict):
            raise LiveControlError("SolidCraft returned an invalid Forge replay result")

        replay_log_data = applied.get("replay_log", {})
        replay_log_text = json.dumps(
            replay_log_data,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        ) + "\n"
        if len(replay_log_text.encode("utf-8")) > MAX_REPLAY_LOG_BYTES:
            raise LiveControlError("Forge live replay log exceeds the evidence size limit")
        replay_log_path = "build/live/replay-log.json"
        _, replay_log = workspace._resolve(replay_log_path)
        replay_log.parent.mkdir(parents=True, exist_ok=True)
        replay_log.write_text(replay_log_text, encoding="utf-8")

        variables = _bounded_result(applied.get("variables", {}))
        response = {
            "ok": True,
            "source": source,
            "compile": compiled,
            "new_design": _bounded_result(fresh) if fresh is not None else None,
            "completed": applied.get("completed"),
            "variables": variables,
            "replay_log": replay_log_path,
        }
    except Exception as exc:
        _record("forge_live", inputs=inputs, ok=False, error=str(exc))
        raise LiveControlError(str(exc)) from exc

    _record("forge_live", inputs=inputs, ok=True, result=response)
    return response

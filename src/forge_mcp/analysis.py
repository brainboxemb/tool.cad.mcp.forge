"""Compact evidence extraction for existing SolidCraft designs and optional JSON inputs."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Mapping

from . import runtime, workspace

MAX_OUTLINE_ROWS = 120


class AnalysisError(ValueError):
    """An existing-design analysis request is invalid or unsupported."""


def _metadata(root: Path, path: Path, kind: str) -> dict:
    return {
        "path": path.relative_to(root).as_posix(),
        "kind": kind,
        "bytes": path.stat().st_size,
        "sha256": workspace._file_sha(path),
    }


def input_summary(path: str) -> dict:
    """Classify one model input without dumping large JSON or native .sc bytes."""
    root, target = workspace._resolve(path, must_exist=True)
    if not target.is_file():
        raise AnalysisError("model_input_summary requires a file")
    suffix = target.suffix.lower()
    if suffix == ".sc":
        return {
            **_metadata(root, target, "solidcraft_native"),
            "text_readable": False,
            "inspect_with": ["solidcraft_analyze", "solidcraft_snapshot"],
        }
    if suffix == ".py":
        return {
            **_metadata(root, target, "forge_python"),
            "text_readable": True,
            "inspect_with": ["workspace_read", "forge_compile"],
        }
    if suffix != ".json":
        raise AnalysisError("model_input_summary supports .sc, .json and .py")

    if target.stat().st_size > workspace.MAX_FILE_BYTES:
        raise AnalysisError("JSON input exceeds the summary size limit")
    try:
        value = json.loads(target.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise AnalysisError("JSON input is not valid UTF-8 JSON") from exc

    result = {
        **_metadata(root, target, "json_unknown"),
        "text_readable": True,
    }
    if isinstance(value, Mapping):
        result["top_level_keys"] = sorted(str(key) for key in value)
        commands = value.get("commands")
        if isinstance(commands, list):
            names = []
            parameters = []
            bodies = []
            for row in commands:
                if not isinstance(row, Mapping):
                    continue
                command = row.get("command")
                if isinstance(command, str):
                    names.append(command)
                params = row.get("params")
                if isinstance(params, Mapping):
                    if command == "parameters.add" and isinstance(params.get("name"), str):
                        parameters.append(params["name"])
                    if isinstance(params.get("body_name"), str):
                        bodies.append(params["body_name"])
            result.update({
                "kind": "solidcraft_command_document",
                "command_count": len(commands),
                "command_types": dict(sorted(Counter(names).items())),
                "parameter_names": list(dict.fromkeys(parameters))[:100],
                "body_names": list(dict.fromkeys(bodies))[:100],
                "inspect_with": ["workspace_read"],
            })
        elif any(key in value for key in ("body_count", "bodies", "params", "timeline", "sketches")):
            result.update({
                "kind": "solidcraft_measurements",
                "sections": sorted(str(key) for key in value),
                "inspect_with": ["workspace_read"],
            })
        elif "results" in value:
            rows = value["results"]
            result.update({
                "kind": "solidcraft_command_results",
                "result_count": len(rows) if isinstance(rows, list) else None,
                "inspect_with": ["workspace_read"],
            })
    elif isinstance(value, list):
        result.update({"kind": "json_array", "items": len(value)})
    return result


def _named_outline(value: Any) -> list[dict]:
    """Extract bounded named structural rows from an unknown component.list envelope."""
    rows: list[dict] = []

    def walk(item: Any, path: str, depth: int) -> None:
        if len(rows) >= MAX_OUTLINE_ROWS or depth > 8:
            return
        if isinstance(item, Mapping):
            if isinstance(item.get("name"), str):
                keep = {
                    key: item[key]
                    for key in (
                        "name", "id", "component", "definition", "grounded", "visible",
                        "body_count", "feature_count", "sketch_count", "bodies", "children",
                    )
                    if key in item
                }
                keep["path"] = path
                rows.append(keep)
            for key, child in item.items():
                walk(child, f"{path}.{key}", depth + 1)
        elif isinstance(item, list):
            for index, child in enumerate(item[:200]):
                walk(child, f"{path}[{index}]", depth + 1)

    walk(value, "$", 0)
    return rows


def analyze(
    model_path: str,
    output_dir: str = "build/analysis",
    include_full_measurements: bool = False,
) -> dict:
    """Collect compact native measurements/history and component structure in one MCP call."""
    root, model = workspace._resolve(model_path, must_exist=True)
    if not model.is_file() or model.suffix.lower() != ".sc":
        raise AnalysisError("solidcraft_analyze requires an existing .sc model")
    _, directory = workspace._resolve(output_dir)
    relative = directory.relative_to(root)
    if not relative.parts or relative.parts[0] != "build":
        raise AnalysisError("solidcraft_analyze output_dir must be below build/")
    if directory.suffix:
        raise AnalysisError("solidcraft_analyze output_dir must be a directory path")

    measurements = runtime.evaluate(
        model_path,
        (relative / "measurements.json").as_posix(),
        include_full_measurements,
    )
    if not measurements.get("ok"):
        return {"ok": False, "model": model.relative_to(root).as_posix(), "measurements": measurements}

    components = runtime.components(
        model_path,
        (relative / "components.json").as_posix(),
        compact=True,
        bodies=True,
    )
    if not components.get("ok"):
        return {
            "ok": False,
            "model": model.relative_to(root).as_posix(),
            "measurements": measurements,
            "components": components,
        }

    return {
        "ok": True,
        "model": model.relative_to(root).as_posix(),
        "solidcraft_version": runtime.SOLIDCRAFT_VERSION,
        "measurements": measurements["summary"],
        "component_outline": _named_outline(components["result"]),
        "artifacts": {
            "measurements": measurements["output"],
            "components": components["output"],
        },
        "full_measurements": measurements.get("measurements") if measurements.get("full_included") else None,
    }

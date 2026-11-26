"""Read-only local readiness diagnostics for Forge MCP."""
from __future__ import annotations

from importlib import metadata

from . import knowledge, runtime, workspace


def doctor(*, include_paths: bool = False) -> dict:
    """Report whether the local MCP authoring stack is ready without executing CAD."""
    result = {
        "ready": False,
        "fastmcp": {"version": metadata.version("fastmcp")},
        "forge": {
            "required_version": knowledge.FORGE_VERSION,
            "required_commit": knowledge.FORGE_COMMIT,
            "ready": False,
        },
        "solidcraft": {
            "required_version": runtime.SOLIDCRAFT_VERSION,
            "ready": False,
        },
        "workspace": {"ready": False},
    }

    try:
        root = knowledge.source_root()
        result["forge"]["ready"] = True
        result["forge"]["version"] = metadata.version("scpf")
        if include_paths:
            result["forge"]["source_root"] = str(root)
    except Exception as exc:
        try:
            result["forge"]["version"] = metadata.version("scpf")
        except metadata.PackageNotFoundError:
            result["forge"]["version"] = None
        result["forge"]["error"] = str(exc)

    try:
        actual = runtime.detect_version()
        result["solidcraft"]["version"] = actual
        result["solidcraft"]["executable"] = runtime.cli_executable() if include_paths else None
        if actual == runtime.SOLIDCRAFT_VERSION:
            result["solidcraft"]["ready"] = True
        else:
            result["solidcraft"]["error"] = (
                f"SolidCraft {actual} differs from required {runtime.SOLIDCRAFT_VERSION}"
            )
    except Exception as exc:
        result["solidcraft"]["version"] = None
        result["solidcraft"]["error"] = str(exc)
    if not include_paths:
        result["solidcraft"].pop("executable", None)

    try:
        status = workspace.status(include_paths=include_paths)
        result["workspace"].update(status)
        result["workspace"]["ready"] = True
    except Exception as exc:
        result["workspace"]["error"] = str(exc)

    result["ready"] = all(
        section["ready"]
        for section in (result["forge"], result["solidcraft"], result["workspace"])
    )
    return result

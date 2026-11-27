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
            "required_ref": knowledge.FORGE_REF,
            "ready": False,
        },
        "solidcraft": {
            "required_version": runtime.SOLIDCRAFT_VERSION,
            "ready": False,
        },
        "workspace": {"ready": False},
    }

    try:
        root = knowledge.validate_source_root()
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


def environment_status() -> dict:
    """Return fast path-free MCP configuration status without subprocess probes."""
    try:
        scpf_version = metadata.version("scpf")
    except metadata.PackageNotFoundError:
        scpf_version = None

    try:
        workspace_status = workspace.status(include_paths=False)
        workspace_ready = True
        workspace_error = None
    except Exception as exc:
        workspace_status = {}
        workspace_ready = False
        workspace_error = str(exc)

    forge_ready = scpf_version == knowledge.FORGE_VERSION
    solidcraft_configured = bool(runtime.cli_executable())
    configured = forge_ready and solidcraft_configured and workspace_ready

    result = {
        "configured": configured,
        "verification": "run forge-cad-mcp doctor for exact Forge checkout and SolidCraft version validation",
        "fastmcp": {"version": metadata.version("fastmcp")},
        "forge": {
            "required_version": knowledge.FORGE_VERSION,
            "required_ref": knowledge.FORGE_REF,
            "installed_version": scpf_version,
            "configured": forge_ready,
        },
        "solidcraft": {
            "required_version": runtime.SOLIDCRAFT_VERSION,
            "configured": solidcraft_configured,
        },
        "workspace": {
            "ready": workspace_ready,
            **workspace_status,
        },
    }
    if workspace_error is not None:
        result["workspace"]["error"] = workspace_error
    return result

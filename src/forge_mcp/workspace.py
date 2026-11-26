"""Bounded target-owner workspace plus read-only catalog dependency access."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

DISCOVER_SUFFIXES = frozenset({".py", ".sc", ".json", ".yml", ".yaml", ".md"})
READ_SUFFIXES = frozenset({".py", ".json", ".yml", ".yaml", ".md"})
WRITE_SUFFIXES = frozenset({".py"})
MAX_FILE_BYTES = 1_000_000
MAX_LIST_LIMIT = 500

_write_enabled = True


class WorkspaceError(ValueError):
    """Workspace or catalog access violates the configured boundary."""


def set_write_enabled(enabled: bool) -> None:
    global _write_enabled
    _write_enabled = bool(enabled)


def _plain_root(value: str, label: str) -> Path:
    raw = Path(value).expanduser()
    if raw.is_symlink():
        raise WorkspaceError(f"{label} may not be a symlink")
    root = raw.resolve()
    if not root.is_dir():
        raise WorkspaceError(f"{label} must be an existing directory")
    return root


def _relative(path: str) -> Path:
    if not isinstance(path, str) or not path.strip():
        raise WorkspaceError("Path must be a non-empty relative path")
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise WorkspaceError("Path must stay inside the configured root")
    return candidate


def _reject_symlinks(root: Path, relative: Path) -> None:
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise WorkspaceError("Configured paths may not traverse symlinks")
        if not current.exists():
            break


def _catalog_binding() -> tuple[Path, Path] | None:
    library_value = os.environ.get("CAD_LIBRARY_ROOT")
    model_value = os.environ.get("CAD_MODEL_ROOT")
    if not library_value and not model_value:
        return None
    if not library_value or not model_value:
        raise WorkspaceError("Set CAD_LIBRARY_ROOT and CAD_MODEL_ROOT together")

    library = _plain_root(library_value, "CAD_LIBRARY_ROOT")
    raw_model = Path(model_value).expanduser()
    candidate = raw_model if raw_model.is_absolute() else library / raw_model
    try:
        lexical_relative = candidate.relative_to(library)
    except ValueError as exc:
        raise WorkspaceError("CAD_MODEL_ROOT must be inside CAD_LIBRARY_ROOT") from exc
    if ".." in lexical_relative.parts:
        raise WorkspaceError("CAD_MODEL_ROOT may not traverse outside CAD_LIBRARY_ROOT")
    _reject_symlinks(library, lexical_relative)

    model = candidate.resolve()
    try:
        relative = model.relative_to(library)
    except ValueError as exc:
        raise WorkspaceError("CAD_MODEL_ROOT must be inside CAD_LIBRARY_ROOT") from exc
    if not model.is_dir():
        raise WorkspaceError("CAD_MODEL_ROOT must be an existing directory")
    if not relative.parts or relative.parts[0] != "models":
        raise WorkspaceError("CAD_MODEL_ROOT must be an owner below CAD_LIBRARY_ROOT/models")
    if not (model / "model.yml").is_file():
        raise WorkspaceError("CAD_MODEL_ROOT must be an exact model owner containing model.yml")
    return library, model


def _root() -> Path:
    binding = _catalog_binding()
    if binding is not None:
        return binding[1]
    configured = os.environ.get("FORGE_WORKSPACE_ROOT")
    if not configured:
        raise WorkspaceError(
            "Set CAD_LIBRARY_ROOT + CAD_MODEL_ROOT, or FORGE_WORKSPACE_ROOT for standalone use"
        )
    return _plain_root(configured, "FORGE_WORKSPACE_ROOT")


def _resolve(path: str, *, must_exist: bool = False) -> tuple[Path, Path]:
    root = _root()
    relative = _relative(path)
    _reject_symlinks(root, relative)
    resolved = (root / relative).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise WorkspaceError("Workspace path escapes configured target owner") from exc
    if must_exist and not resolved.exists():
        raise WorkspaceError("Workspace path does not exist")
    return root, resolved


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def status(*, include_paths: bool = False) -> dict:
    root = _root()
    binding = _catalog_binding()
    result = {
        "write_enabled": _write_enabled,
        "catalog_bound": binding is not None,
        "discover_suffixes": sorted(DISCOVER_SUFFIXES),
        "read_suffixes": sorted(READ_SUFFIXES),
        "write_suffixes": sorted(WRITE_SUFFIXES),
        "max_file_bytes": MAX_FILE_BYTES,
    }
    if binding is not None:
        library, model = binding
        result.update(
            {
                "model_id": model.name,
                "model_relative": model.relative_to(library).as_posix(),
                "dependency_reads": "exact-owner-read-only",
            }
        )
        if include_paths:
            result["root"] = str(model)
            result["cad_library_root"] = str(library)
    elif include_paths:
        result["root"] = str(root)
    return result


def list_files(path: str = ".", limit: int = 200) -> dict:
    root, directory = _resolve(path, must_exist=True)
    if not directory.is_dir():
        raise WorkspaceError("workspace_list path must be a directory")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_LIST_LIMIT:
        raise WorkspaceError(f"limit must be between 1 and {MAX_LIST_LIMIT}")
    rows = []
    for item in sorted(directory.rglob("*")):
        relative = item.relative_to(root)
        if item.is_symlink():
            rows.append({"path": relative.as_posix(), "type": "symlink", "usable": False})
        elif item.is_file() and item.suffix.lower() in DISCOVER_SUFFIXES:
            rows.append({"path": relative.as_posix(), "type": "file", "bytes": item.stat().st_size})
        if len(rows) >= limit:
            break
    return {"path": Path(path).as_posix(), "entries": rows, "truncated": len(rows) >= limit}


def _read_text(root: Path, target: Path, *, display_path: str) -> dict:
    if not target.is_file():
        raise WorkspaceError("Read target must be a file")
    if target.suffix.lower() not in READ_SUFFIXES:
        raise WorkspaceError(
            "File type is not text-readable; inspect native .sc through SolidCraft tools"
        )
    size = target.stat().st_size
    if size > MAX_FILE_BYTES:
        raise WorkspaceError("File exceeds the read size limit")
    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise WorkspaceError("Readable catalog files must be UTF-8 text") from exc
    return {
        "path": display_path,
        "bytes": size,
        "sha256": _file_sha(target),
        "content": content,
    }


def read_file(path: str) -> dict:
    root, target = _resolve(path, must_exist=True)
    return _read_text(root, target, display_path=target.relative_to(root).as_posix())


def _owner_root(owner: str) -> tuple[Path, Path, Path]:
    binding = _catalog_binding()
    if binding is None:
        raise WorkspaceError("Catalog dependency reads require CAD_LIBRARY_ROOT + CAD_MODEL_ROOT")
    library, _ = binding
    relative = _relative(owner)
    if not relative.parts or relative.parts[0] != "models":
        raise WorkspaceError("Dependency owner must be an exact path below models/")
    _reject_symlinks(library, relative)
    owner_root = (library / relative).resolve()
    try:
        owner_root.relative_to(library)
    except ValueError as exc:
        raise WorkspaceError("Dependency owner escapes CAD_LIBRARY_ROOT") from exc
    if not owner_root.is_dir() or not (owner_root / "model.yml").is_file():
        raise WorkspaceError("Dependency owner must be an exact model owner containing model.yml")
    return library, owner_root, relative


def library_read_owner(owner: str, path: str) -> dict:
    """Read one exact file from an explicitly named model owner; never write."""
    _, owner_root, owner_relative = _owner_root(owner)
    relative = _relative(path)
    _reject_symlinks(owner_root, relative)
    target = (owner_root / relative).resolve()
    try:
        target.relative_to(owner_root)
    except ValueError as exc:
        raise WorkspaceError("Dependency path escapes its owner") from exc
    result = _read_text(
        owner_root,
        target,
        display_path=f"{owner_relative.as_posix()}/{target.relative_to(owner_root).as_posix()}",
    )
    result["owner"] = owner_relative.as_posix()
    result["read_only"] = True
    return result


def library_list_owner(owner: str, path: str = ".", limit: int = 200) -> dict:
    """List readable files below one explicitly named dependency owner; never list the catalog."""
    _, owner_root, owner_relative = _owner_root(owner)
    relative = _relative(path)
    _reject_symlinks(owner_root, relative)
    directory = (owner_root / relative).resolve()
    try:
        directory.relative_to(owner_root)
    except ValueError as exc:
        raise WorkspaceError("Dependency path escapes its owner") from exc
    if not directory.is_dir():
        raise WorkspaceError("library_list_owner path must be a directory")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_LIST_LIMIT:
        raise WorkspaceError(f"limit must be between 1 and {MAX_LIST_LIMIT}")
    rows = []
    for item in sorted(directory.rglob("*")):
        item_relative = item.relative_to(owner_root)
        if item.is_symlink():
            rows.append({"path": item_relative.as_posix(), "type": "symlink", "usable": False})
        elif item.is_file() and item.suffix.lower() in DISCOVER_SUFFIXES:
            rows.append({"path": item_relative.as_posix(), "type": "file", "bytes": item.stat().st_size})
        if len(rows) >= limit:
            break
    return {
        "owner": owner_relative.as_posix(),
        "path": relative.as_posix(),
        "entries": rows,
        "truncated": len(rows) >= limit,
        "read_only": True,
    }


def write_source(path: str, content: str, expected_sha256: str | None = None) -> dict:
    if not _write_enabled:
        raise WorkspaceError("Workspace writes are disabled for this server transport")
    root, target = _resolve(path)
    if target.suffix.lower() not in WRITE_SUFFIXES:
        raise WorkspaceError("Only Python Forge source files may be written through MCP")
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_FILE_BYTES:
        raise WorkspaceError("Workspace file exceeds the write size limit")
    if target.exists():
        if not target.is_file():
            raise WorkspaceError("workspace_write target is not a file")
        if expected_sha256 is None:
            raise WorkspaceError("expected_sha256 is required when replacing an existing source file")
        if _file_sha(target) != expected_sha256:
            raise WorkspaceError("Source changed since it was read; expected_sha256 does not match")
    elif expected_sha256 is not None:
        raise WorkspaceError("expected_sha256 must be omitted when creating a new source file")
    target.parent.mkdir(parents=True, exist_ok=True)
    _reject_symlinks(root, target.relative_to(root).parent)
    temporary = target.with_name(f".{target.name}.tmp")
    temporary.write_bytes(encoded)
    temporary.replace(target)
    return {
        "path": target.relative_to(root).as_posix(),
        "bytes": len(encoded),
        "sha256": _file_sha(target),
        "created": expected_sha256 is None,
    }

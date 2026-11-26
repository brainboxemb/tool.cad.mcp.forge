"""Bounded local workspace access for MCP authoring."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

DISCOVER_SUFFIXES = frozenset({".py", ".sc", ".json"})
READ_SUFFIXES = frozenset({".py", ".json"})
WRITE_SUFFIXES = frozenset({".py"})
DEPENDENCY_READ_SUFFIXES = frozenset({".py", ".json", ".yml", ".yaml", ".md"})
MAX_FILE_BYTES = 1_000_000
MAX_LIST_LIMIT = 500
_write_enabled = True

class WorkspaceError(ValueError):
    """Workspace access is unavailable or violates the workspace contract."""

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

def _catalog_binding() -> tuple[Path, Path] | None:
    library_value = os.environ.get("CAD_LIBRARY_ROOT")
    model_value = os.environ.get("CAD_MODEL_ROOT")
    if not library_value and not model_value:
        return None
    if not library_value or not model_value:
        raise WorkspaceError("Set CAD_LIBRARY_ROOT and CAD_MODEL_ROOT together")
    library = _plain_root(library_value, "CAD_LIBRARY_ROOT")
    raw_model = Path(model_value).expanduser()
    if not raw_model.is_absolute():
        raw_model = library / raw_model
    if raw_model.is_symlink():
        raise WorkspaceError("CAD_MODEL_ROOT may not be a symlink")
    model = raw_model.resolve()
    if not model.is_dir():
        raise WorkspaceError("CAD_MODEL_ROOT must be an existing directory")
    try:
        relative = model.relative_to(library)
    except ValueError as exc:
        raise WorkspaceError("CAD_MODEL_ROOT must be inside CAD_LIBRARY_ROOT") from exc
    if not relative.parts:
        raise WorkspaceError("CAD_MODEL_ROOT must select one model folder, not the library root")
    if not (model / "model.yml").is_file():
        raise WorkspaceError("CAD_MODEL_ROOT must be an exact model owner containing model.yml")
    return library, model

def _root() -> Path:
    binding = _catalog_binding()
    if binding is not None:
        return binding[1]
    configured = os.environ.get("FORGE_WORKSPACE_ROOT")
    if not configured:
        raise WorkspaceError("Set CAD_LIBRARY_ROOT + CAD_MODEL_ROOT, or FORGE_WORKSPACE_ROOT for standalone use")
    return _plain_root(configured, "FORGE_WORKSPACE_ROOT")

def _relative(path: str) -> Path:
    if not isinstance(path, str) or not path.strip():
        raise WorkspaceError("Workspace path must be a non-empty relative path")
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise WorkspaceError("Workspace path must stay inside the configured root")
    return candidate

def _reject_symlinks(root: Path, relative: Path) -> None:
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise WorkspaceError("Workspace paths may not traverse symlinks")
        if not current.exists():
            break

def _resolve(path: str, *, must_exist: bool = False) -> tuple[Path, Path]:
    root = _root()
    relative = _relative(path)
    _reject_symlinks(root, relative)
    resolved = (root / relative).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise WorkspaceError("Workspace path escapes configured root") from exc
    if must_exist and not resolved.exists():
        raise WorkspaceError("Workspace path does not exist")
    return root, resolved


def _library_root() -> Path:
    binding = _catalog_binding()
    if binding is None:
        raise WorkspaceError("CAD-library dependency access requires CAD_LIBRARY_ROOT + CAD_MODEL_ROOT")
    return binding[0]


def _catalog_resolve(path: str, *, must_exist: bool = False) -> tuple[Path, Path]:
    library = _library_root()
    relative = _relative(path)
    _reject_symlinks(library, relative)
    resolved = (library / relative).resolve(strict=False)
    try:
        resolved.relative_to(library)
    except ValueError as exc:
        raise WorkspaceError("Catalog path escapes configured CAD library") from exc
    if must_exist and not resolved.exists():
        raise WorkspaceError("Catalog path does not exist")
    return library, resolved


def _owner_root_for(path: Path, library: Path) -> Path | None:
    current = path if path.is_dir() else path.parent
    while current != library:
        if (current / "model.yml").is_file():
            return current
        current = current.parent
    return None


def catalog_dependency_list(owner: str, limit: int = 200) -> dict:
    """List one exact model owner from the CAD library read-only."""
    library, directory = _catalog_resolve(owner, must_exist=True)
    if not directory.is_dir() or _owner_root_for(directory, library) != directory:
        raise WorkspaceError("Dependency owner must be an exact model folder containing model.yml")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_LIST_LIMIT:
        raise WorkspaceError(f"limit must be between 1 and {MAX_LIST_LIMIT}")
    rows = []
    for item in sorted(directory.rglob("*")):
        relative = item.relative_to(library)
        if item.is_symlink():
            rows.append({"path": relative.as_posix(), "type": "symlink", "usable": False})
        elif item.is_file() and (
            item.suffix.lower() in DEPENDENCY_READ_SUFFIXES or item.suffix.lower() == ".sc"
        ):
            rows.append({
                "path": relative.as_posix(),
                "type": "native" if item.suffix.lower() == ".sc" else "file",
                "bytes": item.stat().st_size,
            })
        if len(rows) >= limit:
            break
    return {
        "owner": directory.relative_to(library).as_posix(),
        "entries": rows,
        "truncated": len(rows) >= limit,
        "read_only": True,
    }


def catalog_dependency_read(path: str) -> dict:
    """Read one exact text file inside a model owner elsewhere in the CAD library."""
    library, target = _catalog_resolve(path, must_exist=True)
    if not target.is_file():
        raise WorkspaceError("catalog_dependency_read requires a file")
    owner = _owner_root_for(target, library)
    if owner is None:
        raise WorkspaceError("Dependency file must belong to a model owner containing model.yml")
    if target.suffix.lower() not in DEPENDENCY_READ_SUFFIXES:
        raise WorkspaceError("Dependency file type is not text-readable; inspect native .sc through SolidCraft tools")
    size = target.stat().st_size
    if size > MAX_FILE_BYTES:
        raise WorkspaceError("Dependency file exceeds the read size limit")
    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise WorkspaceError("Dependency files must be UTF-8 text") from exc
    return {
        "owner": owner.relative_to(library).as_posix(),
        "path": target.relative_to(library).as_posix(),
        "bytes": size,
        "sha256": _file_sha(target),
        "content": content,
        "read_only": True,
    }

def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()

def status() -> dict:
    root = _root()
    binding = _catalog_binding()
    result = {
        "root": str(root),
        "write_enabled": _write_enabled,
        "discover_suffixes": sorted(DISCOVER_SUFFIXES),
        "read_suffixes": sorted(READ_SUFFIXES),
        "write_suffixes": sorted(WRITE_SUFFIXES),
        "max_file_bytes": MAX_FILE_BYTES,
        "catalog_bound": binding is not None,
    }
    if binding is not None:
        library, model = binding
        result.update({
            "cad_library_root": str(library),
            "model_id": model.name,
            "model_relative": model.relative_to(library).as_posix(),
        })
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

def read_file(path: str) -> dict:
    root, target = _resolve(path, must_exist=True)
    if not target.is_file():
        raise WorkspaceError("workspace_read requires a file")
    if target.suffix.lower() not in READ_SUFFIXES:
        raise WorkspaceError("File type is not text-readable through the model workspace; inspect native .sc through SolidCraft tools")
    size = target.stat().st_size
    if size > MAX_FILE_BYTES:
        raise WorkspaceError("Workspace file exceeds the read size limit")
    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise WorkspaceError("Workspace files must be UTF-8 text") from exc
    return {"path": target.relative_to(root).as_posix(), "bytes": size, "sha256": _file_sha(target), "content": content}

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
    return {"path": target.relative_to(root).as_posix(), "bytes": len(encoded), "sha256": _file_sha(target), "created": expected_sha256 is None}

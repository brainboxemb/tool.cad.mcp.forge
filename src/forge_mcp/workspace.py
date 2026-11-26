"""Bounded local workspace access for MCP authoring."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

READ_SUFFIXES = frozenset({".py", ".sc", ".json"})
WRITE_SUFFIXES = frozenset({".py"})
MAX_FILE_BYTES = 1_000_000
MAX_LIST_LIMIT = 500

_write_enabled = True


class WorkspaceError(ValueError):
    """Workspace access is unavailable or violates the workspace contract."""


def set_write_enabled(enabled: bool) -> None:
    """Enable source writes for trusted local transport only."""
    global _write_enabled
    _write_enabled = bool(enabled)


def _root() -> Path:
    configured = os.environ.get("FORGE_WORKSPACE_ROOT")
    if not configured:
        raise WorkspaceError("Set FORGE_WORKSPACE_ROOT to an existing local model workspace")
    raw = Path(configured).expanduser()
    if raw.is_symlink():
        raise WorkspaceError("FORGE_WORKSPACE_ROOT may not be a symlink")
    root = raw.resolve()
    if not root.is_dir():
        raise WorkspaceError("FORGE_WORKSPACE_ROOT must be an existing directory")
    return root


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


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def status() -> dict:
    root = _root()
    return {
        "root": str(root),
        "write_enabled": _write_enabled,
        "read_suffixes": sorted(READ_SUFFIXES),
        "write_suffixes": sorted(WRITE_SUFFIXES),
        "max_file_bytes": MAX_FILE_BYTES,
    }


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
        elif item.is_file() and item.suffix.lower() in READ_SUFFIXES:
            rows.append({"path": relative.as_posix(), "type": "file", "bytes": item.stat().st_size})
        if len(rows) >= limit:
            break
    return {"path": Path(path).as_posix(), "entries": rows, "truncated": len(rows) >= limit}


def read_file(path: str) -> dict:
    root, target = _resolve(path, must_exist=True)
    if not target.is_file():
        raise WorkspaceError("workspace_read requires a file")
    if target.suffix.lower() not in READ_SUFFIXES:
        raise WorkspaceError("File type is not readable through the model workspace")
    size = target.stat().st_size
    if size > MAX_FILE_BYTES:
        raise WorkspaceError("Workspace file exceeds the read size limit")
    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise WorkspaceError("Workspace files must be UTF-8 text") from exc
    return {
        "path": target.relative_to(root).as_posix(),
        "bytes": size,
        "sha256": _file_sha(target),
        "content": content,
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
        actual = _file_sha(target)
        if actual != expected_sha256:
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

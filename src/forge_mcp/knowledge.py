"""Read-only, release-matched Forge authoring knowledge."""
from importlib import import_module, metadata
import inspect
import os
from pathlib import Path
import subprocess

FORGE_VERSION = "0.19.0"
FORGE_COMMIT = "ce9cd4439efe51edc360b7bfffb77b950e218d32"


class KnowledgeError(ValueError):
    """The requested knowledge is unavailable or outside the public API."""


def _git(root: Path, *args: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args], check=True, capture_output=True,
            text=True, timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise KnowledgeError("Cannot validate local Forge checkout") from exc


def source_root() -> Path:
    configured = os.environ.get("FORGE_SOURCE_ROOT")
    if not configured:
        raise KnowledgeError("Set FORGE_SOURCE_ROOT to the supported Forge release checkout")
    root = Path(configured).resolve()
    try:
        installed = metadata.version("scpf")
    except metadata.PackageNotFoundError as exc:
        raise KnowledgeError("Install scpf from the supported checkout's cadlib directory") from exc
    if installed != FORGE_VERSION or _git(root, "rev-parse", "HEAD") != FORGE_COMMIT:
        raise KnowledgeError(f"Forge knowledge requires scpf {FORGE_VERSION} at {FORGE_COMMIT}")
    if _git(root, "status", "--porcelain", "--untracked-files=no"):
        raise KnowledgeError("Forge source checkout has tracked modifications")
    return root


def _read(root: Path, path: Path) -> str:
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise KnowledgeError("Knowledge path escapes Forge checkout")
    return resolved.read_text(encoding="utf-8")


def _api():
    source_root()
    return import_module("scpf")


def _summary(obj) -> str:
    return (inspect.getdoc(obj) or "").split("\n", 1)[0]


def _signature(obj) -> str | None:
    try:
        return str(inspect.signature(obj))
    except (TypeError, ValueError):
        return None


def _public_members(obj):
    if inspect.isclass(obj):
        for name in dir(obj):
            if not name.startswith("_"):
                member = getattr(obj, name)
                if callable(member) or isinstance(member, property):
                    yield name, member


def api_lookup(name: str) -> dict:
    api = _api()
    parts = name.split(".")
    if len(parts) not in (1, 2) or parts[0] not in api.__all__:
        raise KnowledgeError("Use an exported Forge name, optionally followed by a public member")
    obj = getattr(api, parts[0])
    if len(parts) == 2:
        members = dict(_public_members(obj))
        if parts[1] not in members:
            raise KnowledgeError("Unknown public Forge member")
        obj = members[parts[1]]
    return {
        "forge_version": FORGE_VERSION, "name": name, "signature": _signature(obj),
        "docstring": (inspect.getdoc(obj) or "")[:8000],
        "members": [key for key, _ in _public_members(obj)],
    }


def example_read(model: str) -> dict:
    root = source_root()
    path = root / "models" / model / "scpf" / "model.py"
    if not path.is_file():
        raise KnowledgeError("Unknown Forge example")
    code = _read(root, path)
    if len(code) > 40000:
        raise KnowledgeError("Example exceeds the current tool response limit")
    return {"forge_version": FORGE_VERSION, "path": str(path.relative_to(root)), "source": code}

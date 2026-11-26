"""Read-only, release-matched Forge authoring knowledge."""
from importlib import import_module, metadata
import inspect
import os
from pathlib import Path
import re
import subprocess
from functools import lru_cache
from html.parser import HTMLParser

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


def _terms(query: str) -> list[str]:
    terms = re.findall(r"[a-z0-9_]+", query.lower())[:12]
    if not terms:
        raise KnowledgeError("Provide a non-empty search query")
    return terms


def _score(terms: list[str], text: str) -> int:
    text = text.lower()
    return sum(term in text for term in terms)


def api_search(query: str, limit: int = 12) -> dict:
    api = _api()
    terms = _terms(query)
    results = []
    for name in api.__all__:
        obj = getattr(api, name)
        for key, value in [(name, obj), *((f"{name}.{n}", m) for n, m in _public_members(obj))]:
            summary = _summary(value)
            score = 3 * _score(terms, key) + _score(terms, summary)
            if score:
                results.append((score, key, {"name": key, "signature": _signature(value), "summary": summary[:500]}))
    results.sort(key=lambda row: (-row[0], row[1]))
    return {"forge_version": FORGE_VERSION, "matches": [row[2] for row in results[:max(1, min(limit, 30))]]}


class _HTMLText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_endtag(self, tag):
        if tag in {"p", "pre", "li", "h1", "h2", "h3", "tr"}:
            self.parts.append("\n")


def _doc_text(root: Path, path: Path) -> str:
    content = _read(root, path)
    if path.suffix == ".html":
        parser = _HTMLText()
        parser.feed(content)
        return "".join(parser.parts)
    return content


@lru_cache(maxsize=4)
def _documents(root: Path) -> tuple:
    docs = root / "docs"
    paths = [docs / "api.md", docs / "api-reference.json", docs / "cheatsheet.yml"]
    paths.extend(sorted((docs / "guide").glob("*.html")))
    chunks = []
    for path in paths:
        lines = _doc_text(root, path).splitlines()
        for start in range(0, len(lines), 18):
            snippet = "\n".join(lines[start:start + 24]).strip()[:2500]
            if snippet:
                chunks.append((str(path.relative_to(root)), snippet))
    return tuple(chunks)


def docs_search(query: str, limit: int = 5) -> dict:
    root = source_root()
    terms = _terms(query)
    ranked = []
    for path, snippet in _documents(root):
        score = _score(terms, snippet) + _score(terms, path)
        if score:
            ranked.append((score, path, snippet))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    return {"forge_version": FORGE_VERSION, "matches": [
        {"path": path, "excerpt": snippet} for _, path, snippet in ranked[:max(1, min(limit, 10))]
    ]}


def example_search(query: str, limit: int = 8) -> dict:
    root = source_root()
    terms = _terms(query)
    results = []
    for path in sorted((root / "models").glob("*/scpf/model.py")):
        name = path.parent.parent.name
        code = _read(root, path)
        score = 3 * _score(terms, name) + _score(terms, code)
        if score:
            results.append((score, name, str(path.relative_to(root))))
    results.sort(key=lambda row: (-row[0], row[1]))
    return {"forge_version": FORGE_VERSION, "matches": [
        {"model": name, "path": path} for _, name, path in results[:max(1, min(limit, 20))]
    ]}


def example_read(model: str) -> dict:
    root = source_root()
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", model):
        raise KnowledgeError("Use an exact example model ID")
    path = root / "models" / model / "scpf" / "model.py"
    if not path.is_file():
        raise KnowledgeError("Unknown Forge example")
    code = _read(root, path)
    if len(code) > 40000:
        raise KnowledgeError("Example exceeds the current tool response limit")
    return {"forge_version": FORGE_VERSION, "path": str(path.relative_to(root)), "source": code}

"""Expose task-oriented MCP skills and release-matched Forge references."""
from importlib.resources import files
import json
import re

from . import knowledge

_SKILLS = {
    "forge-modeling": {
        "description": "Build a new maintainable Python Forge CAD model and prove the generated result.",
        "tools": (
            "environment", "workspace_status", "workspace_list", "workspace_read",
            "workspace_write", "forge_compile", "solidcraft_replay",
            "solidcraft_analyze", "solidcraft_snapshot", "skill_reference",
        ),
    },
    "forge-editing": {
        "description": "Change or fix an existing Python Forge model while preserving its design intent.",
        "tools": (
            "environment", "workspace_status", "workspace_list", "workspace_read",
            "workspace_write", "catalog_dependency_list", "catalog_dependency_read",
            "forge_compile", "solidcraft_replay", "solidcraft_analyze",
            "solidcraft_snapshot", "skill_reference",
        ),
    },
    "forge-checking": {
        "description": "Check Forge output against geometric, structural and visual invariants.",
        "tools": (
            "forge_compile", "solidcraft_replay", "solidcraft_analyze",
            "solidcraft_evaluate", "solidcraft_components", "solidcraft_snapshot",
            "skill_reference",
        ),
    },
    "forge-assemblies": {
        "description": "Compose reusable components, occurrences, attachments and subassemblies.",
        "tools": (
            "environment", "workspace_status", "workspace_list", "workspace_read",
            "workspace_write", "catalog_dependency_list", "catalog_dependency_read",
            "forge_compile", "solidcraft_replay", "solidcraft_analyze",
            "solidcraft_components", "solidcraft_snapshot", "skill_reference",
        ),
    },
    "forge-sheetmetal": {
        "description": "Build or edit Forge sheet-metal models without losing manufacturing intent.",
        "tools": (
            "environment", "workspace_status", "workspace_list", "workspace_read",
            "workspace_write", "forge_compile", "solidcraft_replay",
            "solidcraft_analyze", "solidcraft_snapshot", "skill_reference",
        ),
    },
    "solidcraft-to-forge": {
        "description": "Translate an existing SolidCraft design into maintainable checked Forge Python.",
        "tools": (
            "environment", "workspace_status", "model_input_summary",
            "solidcraft_analyze", "solidcraft_evaluate", "solidcraft_components",
            "solidcraft_snapshot", "workspace_read", "workspace_write",
            "forge_compile", "solidcraft_replay", "skill_reference",
        ),
    },
}

_LOCAL_FILES = frozenset({"SKILL.md", "reference.md"})

_REFS = {
    "references/api.md": "docs/api.md",
    "references/cheatsheet.yml": "docs/cheatsheet.yml",
    "references/solidcraft-commands.md": "docs/reference/solidcraft/0.49.0/commands.md",
}


def skill_list() -> dict:
    return {"skills": [
        {
            "skill": name,
            "description": spec["description"],
            "entrypoint": "SKILL.md",
            "local_reference": "reference.md",
            "tools": list(spec["tools"]),
        }
        for name, spec in _SKILLS.items()
    ]}


def skill_reference(skill: str, file: str = "SKILL.md") -> dict:
    if skill not in _SKILLS:
        raise knowledge.KnowledgeError("Unknown skill; call skill_list")
    if file in _LOCAL_FILES:
        resource = files("forge_mcp").joinpath("skills", skill, file)
        if not resource.is_file():
            raise knowledge.KnowledgeError("Skill reference is not packaged")
        content = resource.read_text(encoding="utf-8")
    elif file == "references/index.json":
        root = knowledge.source_root()
        content = json.dumps({
            "local_files": sorted(_LOCAL_FILES),
            "documents": list(_REFS),
            "guides": [f"references/guide/{p.name}" for p in sorted((root / "docs/guide").glob("*.html"))],
            "examples": [f"references/examples/{p.parent.parent.name}.py" for p in sorted((root / "models").glob("*/scpf/model.py"))],
            "api_symbols": list(knowledge._api().__all__),
            "api_lookup_pattern": "references/api/<Symbol or Symbol.method>.json",
        }, indent=2)
    elif file in _REFS:
        root = knowledge.source_root()
        content = knowledge._read(root, root / _REFS[file])
    elif match := re.fullmatch(r"references/guide/([a-z0-9-]+\.html)", file):
        root = knowledge.source_root()
        content = knowledge._read(root, root / "docs/guide" / match[1])
    elif match := re.fullmatch(r"references/examples/([a-zA-Z0-9][a-zA-Z0-9_-]*)\.py", file):
        content = knowledge.example_read(match[1])["source"]
    elif match := re.fullmatch(r"references/api/([A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)?)\.json", file):
        content = json.dumps(knowledge.api_lookup(match[1]), indent=2)
    else:
        raise knowledge.KnowledgeError("Unknown skill reference; use reference.md or references/index.json")
    return {"skill": skill, "file": file, "forge_version": knowledge.FORGE_VERSION, "content": content}

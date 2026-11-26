"""Expose task-oriented skills and explicit, release-matched references."""
from importlib.resources import files
import json
import re

from . import knowledge

_SKILLS = {
    "forge-modeling": "Author maintainable Python Forge models using the installed release.",
    "solidcraft-to-forge": "Understand an existing native SolidCraft design and translate it into verified Forge Python.",
}

_REFS = {
    "references/api.md": "docs/api.md",
    "references/cheatsheet.yml": "docs/cheatsheet.yml",
    "references/solidcraft-commands.md": "docs/reference/solidcraft/0.49.0/commands.md",
}


def skill_list() -> dict:
    return {"skills": [
        {"skill": name, "description": description, "entrypoint": "SKILL.md"}
        for name, description in _SKILLS.items()
    ]}


def skill_reference(skill: str, file: str = "SKILL.md") -> dict:
    if skill not in _SKILLS:
        raise knowledge.KnowledgeError("Unknown skill; call skill_list")
    if file == "SKILL.md":
        content = files("forge_mcp").joinpath("skills", skill, "SKILL.md").read_text(encoding="utf-8")
    elif file == "references/index.json":
        root = knowledge.source_root()
        content = json.dumps({
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
        raise knowledge.KnowledgeError("Unknown skill reference; use references/index.json")
    return {"skill": skill, "file": file, "forge_version": knowledge.FORGE_VERSION, "content": content}

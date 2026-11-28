"""Export the actual knowledge payloads for human review, never a second API source."""
import json
import os
from pathlib import Path
import re

import pytest

from forge_mcp import skills


def test_export_forge_reference_review(tmp_path):
    destination = os.environ.get("FORGE_REFERENCE_REVIEW_DIR")
    if not destination:
        pytest.skip("Set FORGE_REFERENCE_REVIEW_DIR to export review evidence")

    output = Path(destination)
    output.mkdir(parents=True, exist_ok=True)
    records = []

    def export(skill, file, relative=None):
        response = skills.skill_reference(skill, file)
        target = output / (relative or file)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(response["content"], encoding="utf-8")
        return response

    listing = skills.skill_list()
    (output / "skill-list.json").write_text(
        json.dumps(listing, indent=2), encoding="utf-8"
    )
    for entry in listing["skills"]:
        export(entry["skill"], entry["entrypoint"],
               f"skills/{entry['skill']}/SKILL.md")

    index = json.loads(export("forge-modeling", "references/index.json")["content"])

    def export_api(name):
        response = export("forge-modeling", f"references/api/{name}.json")
        payload = json.loads(response["content"])
        assert payload["name"] == name
        assert payload["forge_version"] == response["forge_version"]
        assert isinstance(payload["docstring"], str)
        assert isinstance(payload["members"], list)
        records.append(payload)
        return payload

    for symbol in index["api_symbols"]:
        payload = export_api(symbol)
        for member in payload["members"]:
            # The resolver exposes one level of public members.
            if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", member):
                export_api(f"{symbol}.{member}")

    by_name = {record["name"]: record for record in records}
    for name in ("Box", "Hole", "Sketch", "Shape.on"):
        assert by_name[name]["signature"]
        assert by_name[name]["docstring"].strip()

    missing_docs = [r["name"] for r in records if not r["docstring"].strip()]
    missing_signatures = [r["name"] for r in records if not r["signature"]]
    report = [
        "# Forge reference review", "",
        f"Forge version: {records[0]['forge_version']}",
        f"API payloads: {len(records)}",
        "",
        "These files contain the actual content returned by skill_reference.",
        "They are generated review evidence, not maintained documentation.",
        "Missing signatures can be normal for constants and non-callables.",
        "Missing docstrings and signatures are review indicators, not a quality verdict.",
        "",
        f"## Missing docstrings ({len(missing_docs)})",
        *(f"- {name}" for name in missing_docs),
        "",
        f"## Missing signatures ({len(missing_signatures)})",
        *(f"- {name}" for name in missing_signatures),
        "",
        "## API content",
    ]
    for record in records:
        report.extend([
            "",
            f"### {record['name']}",
            "",
            "```text",
            str(record["signature"] or "(no signature)"),
            "```",
            "",
            record["docstring"] or "(no docstring)",
        ])
    (output / "REVIEW.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Exported {len(records)} API payloads; "
          f"{len(missing_docs)} missing docstrings; "
          f"{len(missing_signatures)} missing signatures.")
    for name in ("Box", "Hole", "Sketch", "Shape.on"):
        print(f"\n--- references/api/{name}.json ---")
        print((output / f"references/api/{name}.json").read_text(encoding="utf-8"))

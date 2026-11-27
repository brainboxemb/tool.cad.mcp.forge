import base64
import json
from pathlib import Path

import pytest

from forge_mcp import live


PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZQmcAAAAASUVORK5CYII="
)


def _workspace(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("FORGE_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.delenv("CAD_LIBRARY_ROOT", raising=False)
    monkeypatch.delenv("CAD_MODEL_ROOT", raising=False)
    live.set_execution_enabled(True)


def test_live_execute_uses_scpf_control_and_logs_evidence(tmp_path, monkeypatch):
    _workspace(tmp_path, monkeypatch)
    calls = []

    def send_commands(commands, **kwargs):
        calls.append((commands, kwargs))
        return {
            "completed": 1,
            "results": [{"changed": {"length": 60.0}}],
        }

    monkeypatch.setattr(live.scpf_live, "send_commands", send_commands)

    result = live.execute(
        "parameters.change",
        {"name": "length", "expression": 60},
    )

    assert result["ok"] is True
    assert result["command"] == "parameters.change"
    assert result["result"]["changed"]["length"] == 60.0
    assert calls == [(
        [{
            "command": "parameters.change",
            "params": {"name": "length", "expression": 60},
        }],
        {"connect": "auto"},
    )]

    rows = [
        json.loads(line)
        for line in (tmp_path / "build" / "session.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
    ]
    assert rows[-1]["operation"] == "solidcraft_live_execute"
    assert rows[-1]["ok"] is True
    assert "token" not in json.dumps(rows[-1]).lower()


def test_project_file_configures_source_connection_and_evidence(tmp_path, monkeypatch):
    _workspace(tmp_path, monkeypatch)
    (tmp_path / "project.yml").write_text(
        "schema: 1\n"
        "forge:\n"
        "  source: model.py\n"
        "solidcraft:\n"
        "  connect: 27880\n"
        "evidence:\n"
        "  enabled: true\n"
        "  log: build/evidence/live.jsonl\n"
        "  render: build/evidence/model.png\n",
        encoding="utf-8",
    )

    status = live.project_status()
    assert status["forge_source"] == "model.py"
    assert status["solidcraft_connect"] == 27880
    assert status["evidence"]["log"] == "build/evidence/live.jsonl"
    assert status["evidence"]["render"] == "build/evidence/model.png"


def test_live_inspect_uses_document_inspect(tmp_path, monkeypatch):
    _workspace(tmp_path, monkeypatch)
    calls = []

    def request(method, params, **kwargs):
        calls.append((method, params, kwargs))
        return {
            "parameters": [{"name": "length", "value": 60.0}],
            "timeline": [],
            "bodies": ["Plate"],
        }

    monkeypatch.setattr(live.scpf_live, "_send_request", request)

    result = live.inspect()
    assert result["ok"] is True
    assert result["document"]["bodies"] == ["Plate"]
    assert calls[0][0] == "document.inspect"
    assert calls[0][1] == {
        "measure": False,
        "sketch_counts": False,
        "timeline": "summary",
        "bodies": "names",
    }


def test_live_render_returns_png_and_persists_bounded_evidence(tmp_path, monkeypatch):
    _workspace(tmp_path, monkeypatch)

    def request(method, params, **kwargs):
        assert method == "ui.render"
        path = Path(params["path"])
        path.write_bytes(PNG)
        return {
            "renderer": "gpu",
            "camera": {"target": [0, 0, 0], "distance": 100},
        }

    monkeypatch.setattr(live.scpf_live, "_send_request", request)

    data = live.render(width=320, height=240)
    assert data == PNG
    target = tmp_path / "build" / "live" / "model.png"
    assert target.read_bytes() == PNG

    rows = [
        json.loads(line)
        for line in (tmp_path / "build" / "session.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
    ]
    assert rows[-1]["operation"] == "solidcraft_live_render"
    assert rows[-1]["result"]["output"] == "build/live/model.png"
    assert len(rows[-1]["result"]["sha256"]) == 64


def test_forge_live_compiles_then_applies_document_to_gui(tmp_path, monkeypatch):
    _workspace(tmp_path, monkeypatch)
    source = tmp_path / "scpf" / "model.py"
    source.parent.mkdir()
    source.write_text("pass\n", encoding="utf-8")
    calls = []

    def compile_model(source_path, output_path):
        calls.append(("compile", source_path, output_path))
        target = tmp_path / output_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps({
                "version": 2,
                "commands": [{
                    "command": "parameters.add",
                    "params": {
                        "name": "length",
                        "expression": "60",
                        "unit": "mm",
                    },
                }],
            }),
            encoding="utf-8",
        )
        return {
            "ok": True,
            "source": source_path,
            "output": output_path,
            "commands": 1,
        }

    def new_design(name=None, **kwargs):
        calls.append(("new", name, kwargs))
        return {"name": name or "Untitled"}

    def send_document(document, **kwargs):
        calls.append(("send", document, kwargs))
        return {
            "completed": 1,
            "variables": {},
            "replay_log": {"commands": []},
        }

    monkeypatch.setattr(live.compiler, "compile_model", compile_model)
    monkeypatch.setattr(live.scpf_live, "new_design", new_design)
    monkeypatch.setattr(live.scpf_live, "send_document", send_document)

    result = live.forge_live(design_name="Demo plate")

    assert result["ok"] is True
    assert result["completed"] == 1
    assert result["new_design"]["name"] == "Demo plate"
    assert (tmp_path / "build" / "live" / "replay-log.json").is_file()
    assert calls[0] == ("compile", "scpf/model.py", "build/live/solidcraft.json")
    assert calls[1][0] == "new"
    assert calls[2][0] == "send"


def test_live_control_reports_missing_forge_client(tmp_path, monkeypatch):
    _workspace(tmp_path, monkeypatch)
    monkeypatch.setattr(live, "scpf_live", None)
    with pytest.raises(live.LiveControlError, match="requires the qualified Forge/SCPF"):
        live.execute("parameters.list", {})


def test_live_control_can_be_disabled(tmp_path, monkeypatch):
    _workspace(tmp_path, monkeypatch)
    live.set_execution_enabled(False)
    try:
        with pytest.raises(live.LiveControlError, match="disabled"):
            live.execute("parameters.list", {})
    finally:
        live.set_execution_enabled(True)


def test_project_paths_cannot_escape_workspace(tmp_path, monkeypatch):
    _workspace(tmp_path, monkeypatch)
    (tmp_path / "project.yml").write_text(
        "schema: 1\n"
        "forge:\n"
        "  source: ../outside.py\n",
        encoding="utf-8",
    )
    with pytest.raises(Exception, match="inside the configured root"):
        live.project_status()

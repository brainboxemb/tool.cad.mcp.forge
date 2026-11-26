# Forge MCP

Vendor-neutral local MCP server for AI-assisted Python Forge CAD authoring with SolidCraft inspection, rendering and verification.

The qualified local path uses FastMCP 2.14.7, Forge/SCPF 0.19.0 and SolidCraft 0.49.0. The server is AI-client independent; stdio is the normal local transport.

## Local setup

Create one Python environment containing this package and the exact supported Forge library, and keep the matching Forge checkout available for version-matched skills/references:

```sh
git clone https://github.com/brainboxemb/lib.py.solidcraft.forge.git forge-release
git -C forge-release checkout --detach ce9cd4439efe51edc360b7bfffb77b950e218d32
python -m pip install ./forge-release/cadlib
python -m pip install .
```

SolidCraft 0.49.0 must be installed locally. It may be on PATH or supplied explicitly with `--solidcraft-cli`.

Check the complete environment without executing CAD:

```sh
forge-cad-mcp doctor \
  --cad-library /absolute/path/to/cad-library \
  --model-root models/wall-hook \
  --forge-source /absolute/path/to/forge-release \
  --solidcraft-cli /absolute/path/to/solidcraft-cli
```

The command returns JSON and exits successfully only when the workspace, exact Forge release and SolidCraft 0.49.0 are ready.

## MCP client configuration

Use the same stdio server from VS Code, Claude, Codex or another MCP client. Adapt only the client's outer configuration key:

```json
{
  "command": "/absolute/path/to/venv/bin/forge-cad-mcp",
  "args": [
    "--cad-library", "/absolute/path/to/cad-library",
    "--model-root", "models/wall-hook",
    "--forge-source", "/absolute/path/to/forge-release",
    "--solidcraft-cli", "/absolute/path/to/solidcraft-cli"
  ]
}
```

Windows uses the same arguments; point `command` at the environment's `Scripts\\forge-cad-mcp.exe` and use absolute Windows paths.

Environment variables remain supported as alternatives:

- `CAD_LIBRARY_ROOT`
- `CAD_MODEL_ROOT`
- `FORGE_WORKSPACE_ROOT` (standalone fallback)
- `FORGE_SOURCE_ROOT`
- `SOLIDCRAFT_CLI`

Command-line values take precedence for the current server process.

## Skills

Call `skill_list`, then read the relevant `SKILL.md` using `skill_reference`.

- `forge-modeling` — create or edit maintainable Python Forge models.
- `solidcraft-to-forge` — understand an existing native SolidCraft design and translate it into verified Forge Python.

References are matched to Forge 0.19.0. After local setup, model iteration does not require GitHub calls.

## Local authoring loop

The MCP provides bounded tools for source and CAD work:

```text
workspace_list/read/write
        |
        v
forge_compile
        |
        v
solidcraft_replay
        |
        +--> solidcraft_analyze / solidcraft_evaluate
        +--> solidcraft_components
        +--> solidcraft_snapshot -> PNG to the AI
```

For an existing design:

```text
existing .sc -> model_input_summary / solidcraft_analyze
             -> skill: solidcraft-to-forge
             -> Python Forge source
             -> forge_compile -> solidcraft_replay
             -> analyze + render original and candidate
```

Native `.sc` is an engine-owned artifact and is not exposed as raw text. Optional JSON is classified before use. The MCP does not expose arbitrary shell execution or a generic caller-supplied SolidCraft command runner.

## Transport boundary

Local stdio enables workspace writes, Python model compilation and SolidCraft execution.

Streamable HTTP is still a loopback development transport:

```sh
forge-cad-mcp --transport http --port 8000
```

HTTP remains read-only for workspace/execution until authentication, isolated workspaces and sandboxed generated-Python execution are implemented. No separate MCP Docker image is required for local use.

## Development

```sh
python -m pip install -e '.[test]' ./forge-release/cadlib
FORGE_SOURCE_ROOT="$PWD/forge-release" python -m pytest -q tests
```

CI reuses `ghcr.io/brainboxemb/cad-solidcraft:v0.3.6` for real SolidCraft 0.49.0 acceptance rather than publishing another runtime image.

See `docs/plan.md` for unfinished work.


For catalog work, always bind one exact model owner with `--cad-library` + `--model-root`. The MCP never chooses a target model from the catalog itself. All editable/readable workspace paths are relative to that owner folder.

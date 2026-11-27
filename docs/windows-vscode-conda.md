# Windows + VS Code + Conda local setup

This guide configures the qualified local Forge MCP baseline on Windows for the
VS Code Copilot harness. It uses the same stdio server as other MCP clients; no
VS Code extension and no MCP-specific Docker image are required.

Qualified baseline:

- Python 3.12;
- FastMCP 2.14.7;
- Forge/SCPF 0.25.0 from release tag `v0.25.0`;
- SolidCraft 0.49.0;
- local stdio execution.

The commands below use PowerShell.

Use three explicit checkouts:

```text
C:\Dev\SolidCraft\
├── forge-mcp\       # brainboxemb/tool.cad.mcp.forge
├── forge-release\   # brainboxemb/lib.py.solidcraft.forge
└── cad-library\     # brainboxemb/2026-011-02.cad.solidcraft
```

The CAD-library checkout is context only. Every MCP session additionally binds
one exact owner folder such as `models\assemblies\simple_mft_assembly`. That owner becomes the only
workspace for source, build and SolidCraft tools; the AI must not select another
model from the catalog.

## 1. Create the Conda environment

Create and activate a dedicated environment:

```powershell
conda create --name forge-mcp python=3.12 -y
conda activate forge-mcp
python --version
```

Keep the environment dedicated to the MCP and its supported Forge package. The
VS Code MCP configuration will point directly at the installed
`forge-cad-mcp.exe`, so VS Code does not need to activate Conda itself.

## 2. Install the exact Forge checkout

Choose a persistent development directory. This example uses
`C:\Dev\SolidCraft`:

```powershell
New-Item -ItemType Directory -Force C:\Dev\SolidCraft | Out-Null
Set-Location C:\Dev\SolidCraft

git clone https://github.com/brainboxemb/lib.py.solidcraft.forge.git forge-release
git -C forge-release checkout --detach v0.25.0

python -m pip install .\forge-release\cadlib
python -c "import importlib.metadata as m; print(m.version('scpf'))"
```

The last command must print `0.25.0`.

Do not update this checkout independently. The Forge source checkout and the
installed `scpf` package are one qualified pair. Move to another Forge
revision only when this repository explicitly adopts it.

## 3. Install Forge MCP

Clone the stable MCP repository and install it in the same Conda environment:

```powershell
Set-Location C:\Dev\SolidCraft
git clone https://github.com/brainboxemb/tool.cad.mcp.forge.git forge-mcp
git -C forge-mcp switch main

python -m pip install -e .\forge-mcp

git clone https://github.com/brainboxemb/2026-011-02.cad.solidcraft.git cad-library
git -C cad-library switch dev
```

Record the executable path that VS Code must start:

```powershell
$ForgeMcpExe = (Get-Command forge-cad-mcp).Source
$ForgeMcpExe
```

A normal Conda installation resolves this to the environment's
`Scripts\forge-cad-mcp.exe`. Use the path PowerShell reports rather than
guessing the Conda installation directory.

## 4. Locate SolidCraft 0.49.0

If `solidcraft-cli` is already on `PATH`:

```powershell
$SolidCraftCommand = Get-Command solidcraft-cli -ErrorAction SilentlyContinue
$SolidCraftCommand
where.exe solidcraft-cli
```

Use the executable reported by one of these commands. If neither command finds
it, locate `solidcraft-cli.exe` in the installed SolidCraft 0.49.0
installation and use that absolute path. This guide deliberately does not
assume one Windows installation directory.

For the remaining examples:

```powershell
$SolidCraftCli = "C:\absolute\path\to\solidcraft-cli.exe"
```

## 5. Select the exact CAD-library model owner

Configure the catalog checkout plus one exact owner folder:

```powershell
$CadLibrary = "C:\Dev\SolidCraft\cad-library"
$ModelRoot = "models\assemblies\simple_mft_assembly"
$ForgeSource = "C:\Dev\SolidCraft\forge-release"
```

`$ModelRoot` may be relative to the CAD-library checkout. It must resolve to
one existing directory strictly inside that checkout. Do not point it at the
catalog root.

Changing model means explicitly restarting the MCP with a different
`--model-root`. The AI is not allowed to search the catalog for a likely
target or switch owners implicitly.

Assemblies and subassemblies can still reuse components elsewhere in the same
`cad-library` checkout. Those owners are read-only dependencies. The AI may
inspect an exact dependency with `catalog_dependency_list(owner)` or
`catalog_dependency_read(owner, path)`; it may not use those tools to select
a different target.

Existing Python imports such as `from models.components...` are resolved by
Forge's own model import context when the target source lives below the
catalog's `models/` tree. The MCP does not add a separate component loader.

## 6. Run the readiness check

Run `doctor` before configuring VS Code:

```powershell
& $ForgeMcpExe doctor `
  --cad-library $CadLibrary `
  --model-root $ModelRoot `
  --forge-source $ForgeSource `
  --solidcraft-cli $SolidCraftCli
```

The command does not execute a CAD model. It checks the CAD library, exact
target owner, Forge release and SolidCraft CLI version.

A usable catalog-bound installation returns JSON containing:

```json
{
  "ready": true,
  "workspace": {
    "catalog_bound": true,
    "model_id": "simple_mft_assembly",
    "model_relative": "models/assemblies/simple_mft_assembly"
  }
}
```

Do not start model work unless `model_id` and `model_relative` are the owner
you intended.

## 7. Configure the VS Code Copilot harness

For new VS Code Copilot-harness configurations, use the portable
`mcpServers` format.

### Personal/global configuration

Use this when the MCP is for your Windows account across workspaces.

The native Copilot user file is:

- `$COPILOT_HOME\mcp-config.json` when `COPILOT_HOME` is set;
- otherwise `$HOME\.copilot\mcp-config.json`, normally
  `%USERPROFILE%\.copilot\mcp-config.json` on Windows.

You can also use **Chat: Open Customizations > MCP Servers > Add Server** and
choose **Global > Copilot Global**.

An explicit-path configuration looks like this:

```json
{
  "mcpServers": {
    "forgeCad": {
      "type": "stdio",
      "command": "C:\\absolute\\path\\to\\conda\\envs\\forge-mcp\\Scripts\\forge-cad-mcp.exe",
      "args": [
        "--cad-library",
        "C:\\Dev\\SolidCraft\\cad-library",
        "--model-root",
        "models\\assemblies\\simple_mft_assembly",
        "--forge-source",
        "C:\\Dev\\SolidCraft\\forge-release",
        "--solidcraft-cli",
        "C:\\absolute\\path\\to\\solidcraft-cli.exe"
      ],
      "tools": ["*"]
    }
  }
}
```

JSON requires doubled backslashes in Windows paths.

### Workspace configuration

Use a workspace-root `.mcp.json` when the server definition itself belongs
with the workspace. The file still uses top-level `mcpServers`.

Do not commit personal absolute paths. For a shared file, use environment
references and configure those variables on each machine:

```json
{
  "mcpServers": {
    "forgeCad": {
      "type": "stdio",
      "command": "${FORGE_MCP_EXE}",
      "args": [
        "--cad-library",
        "${CAD_LIBRARY_ROOT}",
        "--model-root",
        "${CAD_MODEL_ROOT}",
        "--forge-source",
        "${FORGE_SOURCE_ROOT}",
        "--solidcraft-cli",
        "${SOLIDCRAFT_CLI}"
      ],
      "tools": ["*"]
    }
  }
}
```

Portable Copilot configuration uses `${NAME}`, not the older
VS Code-specific `${env:NAME}` form.

For new Copilot-harness setup, do **not** use `.vscode/mcp.json` as the
recommended configuration. That path belongs to the deprecated Local harness.

## 8. Verify tool discovery in VS Code

1. Select the Copilot harness in VS Code.
2. Run **Chat: Open Customizations** and open **MCP Servers**.
3. Confirm that `forgeCad` is enabled and not in an error state.
4. Start a Copilot chat and explicitly ask it to call the Forge MCP
   `environment` tool.
5. Confirm `cad_ready: true`.
6. Confirm `readiness.workspace.catalog_bound: true` and verify the exact
   `model_id` / `model_relative`.
7. Ask it to call `skill_list`. The result should include
   `forge-modeling` and `solidcraft-to-forge`.
8. Read the relevant `SKILL.md` through `skill_reference` before model work.

MCP tool calls can still require normal Copilot approval. A configuration that
appears in the editor is not sufficient evidence by itself; verify an actual
tool call.

## 9. Basic working flow

For a new Forge model:

```text
skill_list
  -> skill_reference(forge-modeling/SKILL.md)
  -> workspace_read/write
  -> forge_compile
  -> solidcraft_replay
  -> solidcraft_analyze
  -> solidcraft_snapshot
```

For an existing SolidCraft design:

```text
model_input_summary
  -> solidcraft_analyze
  -> skill_reference(solidcraft-to-forge/SKILL.md)
  -> author Python Forge source
  -> forge_compile + solidcraft_replay
  -> analyze/render original and candidate
```

## 10. Updating the local MCP

Update the MCP only from the stable `main` branch:

```powershell
conda activate forge-mcp

git -C C:\Dev\SolidCraft\forge-mcp switch main
git -C C:\Dev\SolidCraft\forge-mcp pull --ff-only
python -m pip install --upgrade C:\Dev\SolidCraft\forge-mcp
```

Then run `doctor` again with the same paths.

Do not automatically update `forge-release`. Its exact revision is part of
the MCP compatibility contract. When the supported Forge version changes,
follow the new repository documentation and reinstall the newly qualified
`cadlib`.

## Troubleshooting

### `doctor` reports Forge not ready

Check both the installed package and source checkout:

```powershell
python -c "import importlib.metadata as m; print(m.version('scpf'))"
git -C C:\Dev\SolidCraft\forge-release rev-parse HEAD
git -C C:\Dev\SolidCraft\forge-release status --short
```

The qualified baseline requires `scpf 0.25.0`, checkout HEAD at release tag
`v0.25.0`, and no tracked modifications.

### `doctor` reports SolidCraft not ready

Run the configured executable directly:

```powershell
& $SolidCraftCli --version
```

It must report SolidCraft `0.49.0`.

### The wrong model appears

Stop the MCP. Check `--cad-library` and `--model-root`, then run `doctor`
again. The target must be below `models\` and contain its own `model.yml`.
Do not ask the AI to search the catalog for the correct owner.

### The MCP starts but CAD is not ready

Call the MCP `environment` tool. Its `readiness` object is intentionally
path-free: verify `model_id` and `model_relative`. Use local `doctor` only
when you need the absolute target/catalog paths for diagnosis.

### VS Code does not show the server

- confirm the Copilot harness is selected;
- confirm the file uses top-level `mcpServers`;
- verify **Chat: Open Customizations > MCP Servers**;
- check that the VS Code `chat.mcp.access` policy permits MCP use;
- verify the `command` path points directly to the Conda environment's
  `forge-cad-mcp.exe`;
- after changing launch paths or environment variables, restart the affected
  MCP server/session so it receives the new environment.

### VS Code is remote or inside a Dev Container

The stdio executable and all referenced paths must exist on the host where the
Copilot harness actually runs. A local Windows path is not automatically
forwarded into another host or container.

## VS Code references

This setup was checked against the current VS Code documentation on
2026-11-26:

- <https://code.visualstudio.com/docs/agents/reference/mcp-configuration>
- <https://code.visualstudio.com/docs/agent-customization/mcp-servers>
- <https://code.visualstudio.com/docs/agents/run/manage-mcp-servers>

The VS Code configuration surface can change independently of the MCP protocol;
recheck these references when updating this guide.

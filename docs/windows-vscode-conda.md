# Windows + VS Code + Conda local setup

This guide configures the qualified local Forge MCP baseline on Windows for the
VS Code Copilot harness. It uses the same stdio server as other MCP clients; no
VS Code extension and no MCP-specific Docker image are required.

Qualified baseline:

- Python 3.12;
- FastMCP 2.14.7;
- Forge/SCPF 0.19.0 from commit
  `ce9cd4439efe51edc360b7bfffb77b950e218d32`;
- SolidCraft 0.49.0;
- local stdio execution.

The commands below use PowerShell.

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
git -C forge-release checkout --detach ce9cd4439efe51edc360b7bfffb77b950e218d32

python -m pip install .\forge-release\cadlib
python -c "import importlib.metadata as m; print(m.version('scpf'))"
```

The last command must print `0.19.0`.

Do not update this checkout independently. The Forge source checkout and the
installed `scpf` package are one qualified pair. Move to another Forge
revision only when this repository explicitly adopts it.

## 3. Install Forge MCP

Clone the stable MCP repository and install it in the same Conda environment:

```powershell
Set-Location C:\Dev\SolidCraft
git clone https://github.com/brainboxemb/tool.cad.mcp.forge.git forge-mcp
git -C forge-mcp switch main

python -m pip install .\forge-mcp
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

## 5. Check out the CAD library and choose the target owner

Use a third checkout for the CAD/model catalog. The example below uses the
current catalog and its development lane:

```powershell
Set-Location C:\Dev\SolidCraft
git clone https://github.com/brainboxemb/2026-011-02.cad.solidcraft.git cad-library
git -C cad-library switch dev

$CadLibrary = "C:\Dev\SolidCraft\cad-library"
$ModelRoot = "models\assemblies\simple_mft_assembly"
$ForgeSource = "C:\Dev\SolidCraft\forge-release"
```

`$ModelRoot` must name one exact owner below `models\` that contains
`model.yml`. It is the only owner the MCP may edit or write build output
under.

Assemblies can still reuse components from elsewhere in the same checkout. The
MCP exposes exact-owner read-only dependency tools for that purpose. For
example, `simple_mft_assembly` imports owners such as
`models/components/simple_mft`, `guide_rail` and
`mounting_rail_m8`. Reading those dependencies does not switch the editing
target.

Native `.sc` files are treated as SolidCraft-owned artifacts and are
understood through SolidCraft analysis/rendering rather than raw text.

## 6. Run the readiness check

Run `doctor` before configuring VS Code:

```powershell
& $ForgeMcpExe doctor `
  --cad-library $CadLibrary `
  --model-root $ModelRoot `
  --forge-source $ForgeSource `
  --solidcraft-cli $SolidCraftCli
```

The command does not execute a CAD model. It checks the exact target owner,
its containing CAD library, the Forge release and the SolidCraft CLI version.
The JSON also reports `model_id` and `model_relative`.

A usable installation returns JSON with:

```json
{
  "ready": true
}
```

The nested `forge`, `solidcraft` and `workspace` objects identify the
failing layer when `ready` is false.

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
5. Confirm `cad_ready: true`, the expected `model_id`, and the expected
   `model_relative`.
6. Ask it to call `skill_list`. The result should include
   `forge-modeling` and `solidcraft-to-forge`.
7. Read the relevant `SKILL.md` through `skill_reference` before model work.

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

Then run `doctor` again with the same CAD-library/model-root paths.

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

The qualified baseline requires `scpf 0.19.0`, commit
`ce9cd4439efe51edc360b7bfffb77b950e218d32`, and no tracked modifications.

### `doctor` reports SolidCraft not ready

Run the configured executable directly:

```powershell
& $SolidCraftCli --version
```

It must report SolidCraft `0.49.0`.

### The MCP starts but CAD is not ready

Call the MCP `environment` tool. Its `readiness` object reports the same
path-free readiness state as `doctor`. Confirm that `model_id` and
`model_relative` identify the intended owner.

### Doctor says the target is not an owner

The selected model root must be inside the configured CAD library, below
`models\`, and contain `model.yml`. Point at the owner directory itself,
not its `scpf\` subdirectory.

### An assembly imports another component

Keep the assembly as the target. Do not start writing into the component owner.
Forge resolves `models.components...` imports from the same catalog checkout.
The AI can inspect that exact dependency owner with `library_read_owner` or
`library_list_owner`, both read-only.

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

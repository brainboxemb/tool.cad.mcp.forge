# Forge CAD MCP — Developer manual

## 1. Purpose

Develop this server locally in VS Code, using Git, Conda, Python and the
repository tests. AI coding assistance from an IDE extension is optional.
No ChatGPT session or connector is required. Read AGENTS.md, the current
main plan, requirements and design before implementing an issue.

The server is not the managed CAD workspace. Users of the workspace should
follow its [manual](https://github.com/brainboxemb/template.cad.mcp.workspace/blob/main/docs/manual.md).
Do not edit the release-pinned ext/mcp checkout in a consumer.

## 2. Local setup (Windows PowerShell)

Install Git, Conda (e.g. Miniforge), VS Code with the Python extension, and
GitHub CLI (gh). Authenticate gh with gh auth login if needed. Install
SolidCraft 0.50.0 for desktop acceptance. From a development parent folder:

~~~powershell
git clone https://github.com/brainboxemb/tool.cad.mcp.forge.git
cd tool.cad.mcp.forge
.\scripts\bootstrap.ps1
code .
~~~

Bootstrap creates forge-mcp-dev (Python 3.12) if absent, obtains the exact
Forge release checkout in the sibling forge-release folder if absent, and
installs the MCP editable with its test extras. Current baseline: MCP
v0.0.9, Forge/SCPF v0.25.0, FastMCP 2.14.7, SolidCraft 0.50.0.
The Python package supports Python 3.11+. The install script reads the
supported Forge ref from knowledge.py and refuses a dirty or mismatched
Forge checkout. It never resets an existing checkout.

Select forge-mcp-dev with Python: Select Interpreter in VS Code. For
debugging/tests in an activated terminal set the source root:

~~~powershell
conda activate forge-mcp-dev
$env:FORGE_SOURCE_ROOT = (Resolve-Path ..\forge-release).Path
~~~

Use .\scripts\update.ps1 after dependency or package metadata changes;
normal source changes use the editable installation. Restart the client
server after changing code. A new compatibility pin requires explicitly
fetching/checking out the new clean Forge tag before update. Never update
a normal consumer to an unqualified branch.

## 3. Source ownership

| Location | Responsibility |
| --- | --- |
| src/forge_mcp/server.py | MCP registration, launch and transport gates |
| workspace.py | Target containment, Python source editing and read-only dependencies |
| knowledge.py, skills.py, skills/ | Release-matched knowledge access and workflow skills |
| compiler.py | Bounded Forge CLI subprocess |
| runtime.py | Saved SolidCraft replay, evaluation, inspection and snapshots |
| live.py | Forge live client, GUI apply/control/render and session evidence |
| analysis.py | Existing-design analysis |
| diagnostics.py | Exact local doctor and cheap configuration status |
| tests/ | Package, protocol and integration tests |
| modules/ci/ | Released-stack acceptance and change scope |
| modules/merge-policy/, modules/branch-cleanup/, modules/release/ | GitHub policy |
| scripts/ | Thin local PowerShell operator entrypoints |

Forge owns modeling and compilation; SolidCraft owns execution and CAD
verification owns CAD checks. Do not duplicate those layers or proxy
SolidCraft MCP. The Forge-owned agent knowledge proposal (#639 upstream)
is pending; MCP #113/#114 are held until its released contract is available.
Current released references still use the pinned Forge checkout and runtime
introspection. Do not add a parallel Forge manual or HTML patcher.

## 4. Local tests and debugging

~~~powershell
.\scripts\test.ps1
.\scripts\test.ps1 -Tests @("tests/test_compiler.py")
.\scripts\test.ps1 -All
~~~

Default: targeted Windows package checks (knowledge, compiler, live,
protocol and script smoke tests) plus all repository policy modules.
-Tests selects package files; -All includes the entire package suite.
Some full-suite tests assume POSIX executable scripts or symlink support.
Use Linux/WSL for CI-equivalent testing if those fixtures fail on Windows;
do not report skipped or failing tests as passed.

For CI-equivalent Linux tests use an equivalent Python 3.12 environment:

~~~bash
python -m pip install -e '.[test]' ../forge-release/cadlib
export FORGE_SOURCE_ROOT="$(cd ../forge-release && pwd)"
python -m pytest -q tests
PYTHONPATH=modules/ci/src python -m unittest discover -s modules/ci/tests
PYTHONPATH=modules/merge-policy/src python -m unittest discover -s modules/merge-policy/tests
PYTHONPATH=modules/branch-cleanup/src python -m unittest discover -s modules/branch-cleanup/tests
PYTHONPATH=modules/release/src python -m unittest discover -s modules/release/tests
~~~

Real runtime/conversion tests are skipped in ordinary pytest. With Docker
and access to the released runtime image use scripts/test.ps1 -Runtime
where Docker paths are supported, or Linux/WSL:

~~~bash
PYTHONPATH=modules/ci/src python -m forge_mcp_ci acceptance
~~~

This uses the existing runtime v0.3.8, one container and generated fixture
directories below build/. No extra MCP image is required.

Use VS Code pytest test debugging with the selected interpreter and
FORGE_SOURCE_ROOT. Breakpoints in the relevant module are preferable to
debug print statements; stdout in a stdio server is reserved for MCP.

## 5. Real local MCP and desktop acceptance

Use a separate scratch model folder and the developer interpreter:

~~~powershell
$Target = (New-Item -ItemType Directory -Force ..\mcp-dev-workbench).FullName
$Cli = "C:\path\to\solidcraft-cli.exe" # replace
.\scripts\doctor.ps1 -Workspace $Target -SolidCraftCli $Cli
conda activate forge-mcp-dev
(Get-Command python).Source
~~~

In the selected client, configure an explicit stdio command using that
absolute Python path and args -m forge_mcp.server --workspace <target>
--forge-source <checkout> --solidcraft-cli <exe>. Restart after edits.
Do not start a bare stdio server and type commands into it. The client
owns the protocol stream. Doctor validates the exact checkout, CLI version
and workspace, not the live GUI. Start SolidCraft and enable its assistant
connection, then verify actual MCP discovery, authoring, forge_live,
inspection, parameter mutation, view/render and evidence. Use an
independent model for skill acceptance, not one copied from the skill.

For timeout diagnosis compare direct python -m scpf scpf/model.py --out
build/direct.json (run from the scratch target), compiler tests, real stdio
and GUI apply in that order. Record exact versions, source SHA, structured
errors and evidence; never log tokens. The v0.0.9 Windows fix was verified
by the operator, but the compile suite does not yet reproduce the full
Windows IDE stdio route automatically.

## 6. Issue, branch, commit and merge

Create or select one GitHub issue. Check the main plan. Describe and review
behavior/architecture changes before implementation. From a clean checkout:

~~~powershell
.\scripts\branch.ps1 -Issue 123 -Name example-change
# edit and review in VS Code
.\scripts\test.ps1
git diff
.\scripts\commit.ps1 -Message "Describe change (#123)" -Files @("src/forge_mcp/compiler.py","tests/test_compiler.py")
.\scripts\pr.ps1 open -Title "Describe change (#123)" -Body "Refs #123. Test evidence: ..."
# review PR and checks
.\scripts\pr.ps1 merge
~~~

The example issue and paths are placeholders. The branch helper fetches
main and refuses a dirty worktree. Commit stages only specified files and
refuses a pre-existing index. PR open pushes the branch; merge waits for
checks and posts /merge, never a direct merge. Verify actual integration
in GitHub. All temporary branches target main. There is no dev lane.
Do not bypass the merge policy. Return to main and pull --ff-only after
integration. Keep plan/handoff on main and record remaining acceptance.

The repository uses one central ci check; docs-only changes run fast,
runtime-sensitive PRs require headless released-stack acceptance. Main
checks are fast; explicit full CI and release run full acceptance.

## 7. Release

Follow [release.md](release.md). After accepting the product changes:

~~~powershell
.\scripts\release.ps1 prepare -Version v0.0.10
# Edit only pyproject.toml project.version and CHANGELOG.md.
.\scripts\commit.ps1 -Message "Prepare release v0.0.10" -Files @("pyproject.toml","CHANGELOG.md")
.\scripts\pr.ps1 open -Title "Prepare release v0.0.10"
.\scripts\pr.ps1 merge
# verify merge and exact-main ci, then:
git switch main
git pull --ff-only
.\scripts\release.ps1 request -Version v0.0.10 -Issue 123
~~~

The version/issue are illustrative. Prepare creates the release branch,
not release metadata; review and edit those two files explicitly. Request
checks the local branch, current remote main SHA and package version, then
posts /release on the normal release issue. The workflow validates green CI,
metadata and the full runtime acceptance and publishes. Check the issue and
Actions; the script does not create tags or releases directly. Consumer
dependency adoption is separate after publication.

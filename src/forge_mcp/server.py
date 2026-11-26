"""Vendor-neutral MCP entry point; CAD adapters are not yet connected."""
import argparse
import base64
import json
import os
from importlib.metadata import version

from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from . import analysis, compiler, diagnostics, runtime, skills, workspace

mcp = FastMCP("Forge CAD", instructions="Start CAD work by calling skill_list and reading the relevant SKILL.md through skill_reference. The configured target owner is authoritative for edits. Assemblies may inspect explicitly referenced dependency owners through read-only library tools, but never fuzzy-search, switch, or edit another owner implicitly.")

# Fixed transport diagnostic only; never evidence of a CAD render.
_DIAGNOSTIC_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAAGUlEQVR4nGM0SlnAQApgIkn1qIZRDUNKAwDmwwFWY/Xh+wAAAABJRU5ErkJggg=="
)

@mcp.tool
def environment() -> dict:
    """Report protocol and local CAD readiness without executing model work."""
    readiness = diagnostics.doctor(include_paths=False)
    return {
        "protocol": "mcp",
        "stage": "local-qualified",
        "cad_ready": readiness["ready"],
        "fastmcp_version": version("fastmcp"),
        "transports": ["stdio", "streamable-http"],
        "readiness": readiness,
    }

@mcp.tool
def diagnostic_image() -> Image:
    """Return a tiny fixed PNG to check client image support, not a CAD render."""
    return Image(data=_DIAGNOSTIC_PNG, format="png")

@mcp.tool
def skill_list() -> dict:
    """Discover task-oriented skills. Read the relevant SKILL.md before authoring or converting CAD."""
    return skills.skill_list()

@mcp.tool
def skill_reference(skill: str, file: str = "SKILL.md") -> dict:
    """Read a skill entrypoint or a named reference from its references/index.json."""
    return skills.skill_reference(skill, file)

@mcp.tool
def workspace_status() -> dict:
    """Describe the configured local model workspace and edit policy."""
    return workspace.status()

@mcp.tool
def workspace_list(path: str = ".", limit: int = 200) -> dict:
    """List readable model/source files below one workspace directory without following symlinks."""
    return workspace.list_files(path, limit)

@mcp.tool
def workspace_read(path: str) -> dict:
    """Read one UTF-8 source/metadata file from the configured target owner."""
    return workspace.read_file(path)

@mcp.tool
def library_list_owner(owner: str, path: str = ".", limit: int = 200) -> dict:
    """List files below one explicitly named model owner in the same CAD library, read-only."""
    return workspace.library_list_owner(owner, path, limit)

@mcp.tool
def library_read_owner(owner: str, path: str) -> dict:
    """Read one file from one explicitly named model owner in the same CAD library, read-only."""
    return workspace.library_read_owner(owner, path)

@mcp.tool
def workspace_write(path: str, content: str, expected_sha256: str | None = None) -> dict:
    """Create Python Forge source or replace it using the hash returned by workspace_read."""
    return workspace.write_source(path, content, expected_sha256)

@mcp.tool
def model_input_summary(path: str) -> dict:
    """Classify .sc/.json/.py model input compactly before deciding how to inspect it."""
    return analysis.input_summary(path)

@mcp.tool
def solidcraft_analyze(
    model_path: str,
    output_dir: str = "build/analysis",
    include_full_measurements: bool = False,
) -> dict:
    """Collect compact geometry/parameter/history and component evidence for an existing native design."""
    return analysis.analyze(model_path, output_dir, include_full_measurements)

@mcp.tool
def forge_compile(source_path: str, output_path: str = "build/solidcraft.json") -> dict:
    """Compile trusted local workspace Python Forge source to command JSON without starting SolidCraft."""
    return compiler.compile_model(source_path, output_path)

@mcp.tool
def solidcraft_replay(
    commands_path: str = "build/solidcraft.json",
    native_path: str = "build/model.sc",
) -> dict:
    """Replay generated build JSON into a native SolidCraft .sc model."""
    return runtime.replay(commands_path, native_path)

@mcp.tool
def solidcraft_evaluate(
    model_path: str,
    output_path: str = "build/measurements.json",
    include_full: bool = False,
) -> dict:
    """Evaluate a native SolidCraft model and return compact measurements/history evidence."""
    return runtime.evaluate(model_path, output_path, include_full)

@mcp.tool
def solidcraft_components(
    model_path: str,
    output_path: str = "build/components.json",
    compact: bool = True,
    bodies: bool = False,
) -> dict:
    """Inspect native component/occurrence structure using fixed read-only component.list."""
    return runtime.components(model_path, output_path, compact, bodies)

@mcp.tool
def solidcraft_snapshot(
    model_path: str,
    output_path: str = "build/model.png",
    width: int = 800,
    height: int = 600,
    camera: dict | None = None,
) -> Image:
    """Render a native SolidCraft model to a PNG that the MCP client can inspect visually."""
    return Image(data=runtime.snapshot(model_path, output_path, width, height, camera), format="png")

def _configure(args) -> None:
    if args.cad_library and args.model_root:
        os.environ["CAD_LIBRARY_ROOT"] = args.cad_library
        os.environ["CAD_MODEL_ROOT"] = args.model_root
        os.environ.pop("FORGE_WORKSPACE_ROOT", None)
    elif args.workspace:
        os.environ["FORGE_WORKSPACE_ROOT"] = args.workspace
        os.environ.pop("CAD_LIBRARY_ROOT", None)
        os.environ.pop("CAD_MODEL_ROOT", None)
    if args.forge_source:
        os.environ["FORGE_SOURCE_ROOT"] = args.forge_source
    if args.solidcraft_cli:
        os.environ["SOLIDCRAFT_CLI"] = args.solidcraft_cli
    runtime.set_cli_executable(args.solidcraft_cli)


def main() -> None:
    parser = argparse.ArgumentParser(description="Forge CAD MCP server")
    parser.add_argument("mode", nargs="?", choices=["serve", "doctor"], default="serve")
    parser.add_argument("--workspace", help="Standalone workspace root; use only for non-catalog work")
    parser.add_argument("--cad-library", help="Concrete CAD/model catalog checkout")
    parser.add_argument("--model-root", help="Exact target owner below models/ containing model.yml; may be relative to --cad-library")
    parser.add_argument("--forge-source", help="Exact supported Forge release checkout")
    parser.add_argument("--solidcraft-cli", help="SolidCraft CLI executable path or command")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if bool(args.cad_library) != bool(args.model_root):
        parser.error("--cad-library and --model-root must be supplied together")
    if args.workspace and (args.cad_library or args.model_root):
        parser.error("--workspace cannot be combined with --cad-library/--model-root")
    _configure(args)

    if args.mode == "doctor":
        report = diagnostics.doctor(include_paths=True)
        print(json.dumps(report, indent=2))
        raise SystemExit(0 if report["ready"] else 1)

    workspace.set_write_enabled(args.transport == "stdio")
    compiler.set_execution_enabled(args.transport == "stdio")
    runtime.set_execution_enabled(args.transport == "stdio")
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        # Remote bootstrap is read-only until authentication and isolated workspaces exist.
        mcp.run(transport="http", host="127.0.0.1", port=args.port, path="/mcp")

if __name__ == "__main__":
    main()

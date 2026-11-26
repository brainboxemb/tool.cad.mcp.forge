"""Vendor-neutral MCP entry point; CAD adapters are not yet connected."""
import argparse
import base64
from importlib.metadata import version

from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from . import skills, workspace

mcp = FastMCP("Forge CAD", instructions="Start CAD work by calling skill_list and reading the relevant SKILL.md through skill_reference.")

# Fixed transport diagnostic only; never evidence of a CAD render.
_DIAGNOSTIC_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAAGUlEQVR4nGM0SlnAQApgIkn1qIZRDUNKAwDmwwFWY/Xh+wAAAABJRU5ErkJggg=="
)

@mcp.tool
def environment() -> dict:
    """Report available capabilities without claiming unconnected CAD support."""
    return {
        "protocol": "mcp",
        "stage": "bootstrap",
        "cad_ready": False,
        "fastmcp_version": version("fastmcp"),
        "transports": ["stdio", "streamable-http"],
        "workspace_configured": bool(__import__("os").environ.get("FORGE_WORKSPACE_ROOT")),
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
    """Read one UTF-8 Python, SolidCraft .sc or JSON model file with a content hash."""
    return workspace.read_file(path)

@mcp.tool
def workspace_write(path: str, content: str, expected_sha256: str | None = None) -> dict:
    """Create Python Forge source or replace it using the hash returned by workspace_read."""
    return workspace.write_source(path, content, expected_sha256)

def main() -> None:
    parser = argparse.ArgumentParser(description="Forge CAD MCP server")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    workspace.set_write_enabled(args.transport == "stdio")
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        # Remote bootstrap is read-only until authentication and per-client isolation exist.
        mcp.run(transport="http", host="127.0.0.1", port=args.port, path="/mcp")

if __name__ == "__main__":
    main()

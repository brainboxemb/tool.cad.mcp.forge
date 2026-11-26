"""Vendor-neutral MCP entry point; CAD adapters are not yet connected."""
import argparse
import base64
from importlib.metadata import version

from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from . import skills

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

def main() -> None:
    parser = argparse.ArgumentParser(description="Forge CAD MCP server")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        # Remote exposure requires authentication and isolated execution.
        mcp.run(transport="http", host="127.0.0.1", port=args.port, path="/mcp")

if __name__ == "__main__":
    main()

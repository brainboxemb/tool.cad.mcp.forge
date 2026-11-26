"""Thin MCP entry point; CAD adapters are not yet connected."""
from fastmcp import FastMCP

mcp = FastMCP("Forge CAD")

@mcp.tool
def environment() -> dict:
    """Report available capabilities without claiming unconnected CAD support."""
    return {"protocol": "mcp", "stage": "bootstrap", "cad_ready": False}

def main() -> None:
    mcp.run()

if __name__ == "__main__":
    main()

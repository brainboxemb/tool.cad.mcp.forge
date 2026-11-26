# Forge MCP

Vendor-neutral MCP server for AI-assisted Python Forge CAD authoring and SolidCraft runtime inspection, rendering and verification.

Experimental bootstrap; CAD execution is not available yet.

## Local development

```sh
python -m pip install -e '.[test]'
python -m pytest -q
forge-cad-mcp
```

Local MCP client configuration (adapt the enclosing configuration key to the client):

```json
{
  "command": "forge-cad-mcp",
  "args": []
}
```

Streamable HTTP development endpoint:

```sh
forge-cad-mcp --transport http --port 8000
```

Connect to http://127.0.0.1:8000/mcp. Loopback only; not a public deployment. Call environment and diagnostic_image to check client support. The diagnostic image is not a CAD render.

See docs/plan.md for current work.
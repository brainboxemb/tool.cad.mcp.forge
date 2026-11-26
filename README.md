# Forge MCP

Vendor-neutral MCP server for AI-assisted Python Forge CAD authoring and SolidCraft runtime inspection, rendering and verification.

Experimental bootstrap; CAD execution is not available yet.

## Local development

```sh
python -m pip install -e '.[test]'
python -m pytest -q tests  # after Forge setup below
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

## Forge authoring knowledge

Install the matching local Forge release before using the knowledge tools:

```sh
git clone https://github.com/brainboxemb/lib.py.solidcraft.forge.git forge-release
git -C forge-release checkout --detach ce9cd4439efe51edc360b7bfffb77b950e218d32
python -m pip install ./forge-release/cadlib
export FORGE_SOURCE_ROOT="$PWD/forge-release"
```

For a Windows MCP client set FORGE_SOURCE_ROOT to the absolute checkout path in its environment configuration. Use forge_api_lookup, forge_api_search, forge_docs_search, forge_examples_search and forge_example_read. Queries run locally; no GitHub access is needed after setup. CAD compilation is not connected yet.

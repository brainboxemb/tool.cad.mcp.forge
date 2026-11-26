# Design

FastMCP is the protocol adapter. Python Forge code is the authoring artifact. Forge owns compilation; direct SolidCraft CLI calls provide additional runtime operations. Existing verification libraries provide geometric checks. No direct SCPC dependency and no SolidCraft MCP proxy.

Start with a stdio-capable server and an in-process MCP client smoke test. Discover actual installed API and CLI contracts before implementing CAD adapters. Remote transport, authentication and execution isolation are separate acceptance gates; no public remote execution in the bootstrap.

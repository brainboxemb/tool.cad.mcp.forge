# Design

FastMCP is the protocol adapter. Python Forge code is the authoring artifact. Forge owns compilation; direct SolidCraft CLI calls provide additional runtime operations. Existing verification libraries provide geometric checks. No direct SCPC dependency and no SolidCraft MCP proxy.

The same tool interface is exposed over stdio (default) and Streamable HTTP (loopback only during bootstrap). No provider-specific SDK or LLM inference belongs in the server. A fixed diagnostic image tests protocol image delivery independently of the CAD engine; it is never CAD evidence. CI exercises in-process calls, real stdio subprocess calls and two simultaneous HTTP client sessions.

Discover actual installed API and CLI contracts before implementing CAD adapters. Remote authentication, per-client workspace isolation, execution sandboxing and real client compatibility are separate acceptance gates. No public remote execution in the bootstrap.

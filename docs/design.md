# Design

FastMCP is the protocol adapter. Python Forge code is the authoring artifact. Forge owns compilation; direct SolidCraft CLI calls provide additional runtime operations. Existing verification libraries provide geometric checks. No direct SCPC dependency and no SolidCraft MCP proxy.

The same tool interface is exposed over stdio (default) and Streamable HTTP (loopback only during bootstrap). No provider-specific SDK or LLM inference belongs in the server. A fixed diagnostic image tests protocol image delivery independently of the CAD engine; it is never CAD evidence. CI exercises in-process calls, real stdio subprocess calls and two simultaneous HTTP client sessions.

Discover actual installed API and CLI contracts before implementing CAD adapters. Remote authentication, per-client workspace isolation, execution sandboxing and real client compatibility are separate acceptance gates. No public remote execution in the bootstrap.

## Forge knowledge

The initial supported Forge release is v0.19.0, commit ce9cd4439efe51edc360b7bfffb77b950e218d32. Install scpf from that checkout's cadlib directory and configure FORGE_SOURCE_ROOT to the checkout. Knowledge validates the installed distribution version and local checkout commit and rejects tracked checkout modifications. It does not fetch anything at request time. The install procedure and CI use the same checkout; a matching version alone is not a cryptographic proof of installed wheel provenance.

Public signatures and docstrings come from scpf's public exports and their public class members. Only explicit exported names and one public member are resolved; no arbitrary expressions or imports. Documentation searches return bounded, ranked text excerpts from the release's API contract, generated reference, cheatsheet and guide files. Examples are discovered under models/*/scpf/model.py and read by exact model ID. The trusted checkout is read-only from MCP. Report missing configuration or version mismatch explicitly. No generated Python is executed by knowledge tools.

Docker packaging, if useful for an operator hosting MCP or reproducing runtime dependencies, is a later optional deployment decision. Local stdio usage needs no Docker packaging of the MCP itself.

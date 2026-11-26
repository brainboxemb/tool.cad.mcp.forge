# Requirements

- The AI writes and maintains Python Forge source, not a replacement CAD DSL.
- Provide version-matched API knowledge and examples.
- Compile using Forge and invoke additional SolidCraft CLI commands directly for inspection, analysis, rendering and exports.
- Return actual images via MCP and structured verification results.
- Compare original SolidCraft models and generated models using existing CAD verification where applicable.
- Keep local iteration independent of GitHub; GitHub is for source control and qualification.
- Support standard MCP stdio and Streamable HTTP without vendor AI SDKs or embedded LLM inference.
- Verify discovery, structured results and image content over both transports; test independent simultaneous clients.
- Before remote deployment, authenticate clients, isolate generated Python execution and restrict each client's workspace. Transport tests do not prove workspace isolation.
- Qualify through real MCP client tests and real runtime integration tests.

- Knowledge queries use only a locally configured release-matched Forge checkout and installed scpf; no per-query network requests.
- Expose task-oriented SKILL.md entrypoints via skill discovery and skill_reference. Provide explicit references to release-matched API signatures, docstrings, guides, cheatsheet and example source, with explicit errors for unsupported paths or mismatched releases.
- Local stdio installation must remain possible without a new MCP Docker image.
- A conversion skill must teach analysis of existing .sc designs and optional JSON exports, preserving original files and distinguishing observed model data from inferred modeling intent. Actual runtime conversion acceptance belongs to #5.

- A local workspace is configured explicitly with FORGE_WORKSPACE_ROOT; no repository or user home directory is inferred.
- Workspace reads are bounded to UTF-8 .py, .sc and .json files below that root and must not follow symlinks or traversal paths.
- MCP source editing writes only .py files. Existing source replacement requires the exact SHA-256 returned by workspace_read. Native .sc and JSON inputs are read-only through the editor.
- The supported HTTP bootstrap transport exposes no workspace writes; writable remote work requires authentication and per-client isolation first.

- forge_compile accepts only an existing workspace .py source, validates the configured Forge release, and writes command JSON only below build/.
- Compilation invokes the supported scpf module directly without a shell. Compile failures return bounded structured stdout/stderr and remove stale output.
- Python model execution is enabled only for the trusted local stdio transport; the HTTP bootstrap may not compile generated Python.

- SolidCraft execution uses exactly the released 0.49.0 CLI and is local-stdio-only at this stage.
- solidcraft_replay accepts generated command JSON below build/ and writes a native .sc only below build/.
- solidcraft_evaluate accepts an existing workspace .sc, persists measurements below build/, and returns compact parameters/body/history/sketch evidence; optional full evidence is size-bounded.
- solidcraft_snapshot accepts an existing workspace .sc, writes PNG only below build/, validates dimensions/output and returns the PNG through MCP for visual analysis.
- No generic arbitrary SolidCraft command runner is exposed. Native source files are inspected through engine-owned eval/render operations.

- solidcraft_components uses only the internally generated read-only component.list command, never caller-supplied command JSON, and returns its structured result below build/.

- Native .sc files are discoverable workspace artifacts but are not exposed as raw text; use SolidCraft analysis/rendering to understand them.
- model_input_summary classifies .sc/.py and bounded JSON inputs and summarizes command-document types/parameters/body names without dumping the full document.
- solidcraft_analyze combines compact eval evidence and fixed component.list evidence in one call so conversion work does not need to pull full model JSON by default.
- End-to-end conversion acceptance must start from a native design produced independently of Forge, then prove an independently authored Forge model matches required parameters, body geometry and a common visual view.

- Local startup accepts explicit --workspace, --forge-source and --solidcraft-cli arguments; existing environment variables remain fallback configuration.
- forge-cad-mcp doctor validates workspace, exact Forge/SCPF 0.19.0 release and SolidCraft 0.49.0 version without executing a model and exits non-zero when the stack is not ready.
- The MCP environment tool reports the same path-free readiness contract so a client can decide whether CAD work is available.
- The first qualified dependency baseline pins FastMCP 2.14.7 rather than floating across untested 2.x releases.
- One installed server command and argument list must work for any stdio-capable MCP client; no client-specific extension is required.


- Catalog-backed sessions use `CAD_LIBRARY_ROOT` plus `CAD_MODEL_ROOT` (CLI: `--cad-library` + `--model-root`). The target must be an exact owner below `models/` containing `model.yml`.
- The target owner is the only workspace write/build-output scope. The AI must not fuzzy-search for another target, choose a similarly named owner, or switch targets implicitly.
- The same CAD library is a bounded read-only dependency scope. `library_read_owner` and `library_list_owner` accept one explicit owner path containing `model.yml`; they never write or list the whole catalog.
- Assemblies/subassemblies may import component owners from the same catalog. Real compilation acceptance must prove a cross-owner `models.components.*` import succeeds from the selected target.
- Normal MCP readiness/status reports target model id and library-relative owner path without absolute filesystem paths. CLI doctor may include paths for local diagnosis.
- Explicit `--workspace` standalone configuration clears inherited catalog binding for that server process; explicit catalog arguments clear the standalone workspace fallback.

# Design

FastMCP is the protocol adapter. Python Forge code is the authoring artifact. Forge owns compilation; direct SolidCraft CLI calls provide additional runtime operations. Existing verification libraries provide geometric checks. No direct SCPC dependency and no SolidCraft MCP proxy.

The same tool interface is exposed over stdio (default) and Streamable HTTP (loopback only during bootstrap). No provider-specific SDK or LLM inference belongs in the server. A fixed diagnostic image tests protocol image delivery independently of the CAD engine; it is never CAD evidence. CI exercises in-process calls, real stdio subprocess calls and two simultaneous HTTP client sessions.

Discover actual installed API and CLI contracts before implementing CAD adapters. Remote authentication, per-client workspace isolation, execution sandboxing and real client compatibility are separate acceptance gates. No public remote execution in the bootstrap.

## Forge knowledge

The supported Forge release is v0.25.0. Install scpf from that tagged checkout's cadlib directory and configure FORGE_SOURCE_ROOT to the checkout. Knowledge validates the installed distribution version and requires the checkout HEAD to resolve from the local v0.25.0 tag; it also rejects tracked checkout modifications. It does not fetch anything at request time. The install procedure and CI use the same checkout; a matching version alone is not a cryptographic proof of installed wheel provenance.

Skills are the primary knowledge interface, following the SolidCraft skill-reference pattern. Expose only skill_list and skill_reference for knowledge; no separate search tool family. Each packaged SKILL.md teaches a task workflow, followed by explicit references. The initial MCP-owned workflow skills are forge-modeling and solidcraft-to-forge; Forge remains owner of API semantics, guides, cheatsheet and examples. A later Forge-side skill move can be coordinated when reusable ownership is established. References are resolved from an explicit allowlist or constrained symbol/example/guide paths in the validated checkout. Public signatures/docstrings come from installed scpf. The reference index is discoverable, and no arbitrary filesystem access or generated Python execution is provided. The conversion skill describes the intended workflow; actual native model analysis and comparison are gated by #5.

Docker packaging, if useful for an operator hosting MCP or reproducing runtime dependencies, is a later optional deployment decision. Local stdio usage needs no Docker packaging of the MCP itself.

## Local model workspace

FORGE_WORKSPACE_ROOT names one explicit existing directory. Workspace tools expose status, bounded recursive listing, text reads and Python-source writes. Path resolution rejects absolute/traversal paths and symlink traversal. Discovery covers .py, .sc, .json, .yml/.yaml and .md. Text reads are limited to .py, .json, .yml/.yaml and .md and one megabyte per file; native .sc remains opaque. Source writes are limited to .py, use atomic replacement and require an optimistic SHA-256 token when replacing existing content. There is no delete, rename, shell or arbitrary-file tool.

Native .sc and JSON inputs remain immutable through the MCP editor; metadata/docs are readable but not writable. Runtime/build tools may later create generated artifacts through their own bounded interfaces. The CLI enables workspace writes only for stdio. Streamable HTTP remains read-only until authenticated, per-client workspaces and execution isolation are implemented.

## Forge compilation

forge_compile is the only initial model-execution boundary. It validates the same Forge v0.25.0 release used by skill references, resolves one existing workspace .py source, and invokes the supported `python -m scpf <source> --out <build/...json>` interface without a shell. The process runs with the workspace as cwd, has a fixed timeout and bounded captured diagnostics. Before each attempt it removes the previous target so a failed build cannot leave stale command evidence.

Successful output must be a non-empty JSON object with a commands array; the tool returns command count, size and SHA-256. Compile/model errors are normal structured results with ok=false, while invalid workspace/configuration requests remain tool errors. Running a Forge model executes Python and is therefore permitted only for local stdio during this stage. Remote execution requires the later sandbox/authentication gate.

## SolidCraft runtime

The first runtime adapter deliberately exposes only three engine-owned operations: replay generated build command JSON, evaluate an existing native .sc, and render a deterministic PNG. It validates solidcraft-cli 0.49.0 before every operation and uses fixed subprocess argument lists, timeouts, bounded diagnostics and build-only outputs. There is no generic command JSON executor in the MCP interface.

solidcraft_replay accepts only generated JSON below build/ and creates build/*.sc. solidcraft_evaluate may read any workspace .sc without treating the native format as text; it writes build/*.json and returns a compact summary of available sections, bodies, parameters, timeline, sketches and component/occurrence rows when present. Full measurements are optional and size-bounded. solidcraft_snapshot reads any workspace .sc, writes build/*.png and returns the validated PNG as MCP image content.

Runtime execution is enabled only for local stdio. CI creates command JSON with the already-qualified Forge compiler on the host, then runs the MCP runtime acceptance inside the existing ghcr.io/brainboxemb/cad-solidcraft:v0.3.6 image. This proves the same SolidCraft 0.49.0 runtime used by Forge/CAD-CI without introducing a new MCP runtime image.

The fixed solidcraft_components inspection is the first explicit native-structure query. It internally generates exactly one component.list command with boolean compact/bodies options, runs it read-only against the supplied .sc without --save, removes the temporary command file, persists only the result JSON below build/ and returns that result. This does not create a generic command execution surface.

## Existing-design analysis

Native .sc is an opaque engine-owned artifact. Workspace discovery includes .sc, but workspace_read is limited to textual .py/.json. model_input_summary hashes all three supported input types, classifies native/Forge/JSON inputs and, for bounded JSON, identifies command documents, measurement objects or result envelopes. Command summaries expose only command-type counts plus declared parameter/body names; they never execute caller JSON.

solidcraft_analyze is the normal first call for an existing .sc. It composes the already-bounded evaluate and fixed component.list operations, stores their evidence below one build analysis directory, and returns compact measurement/history plus a bounded named component outline. Full measurements remain opt-in and size-bounded.

The #5 acceptance fixture is deliberately not generated by Forge. A hand-authored SolidCraft command document creates the original native box. A separate parameterized Forge Python model compiles to candidate command JSON. Inside the released SolidCraft 0.49.0 runtime, MCP analysis proves equal parameter values, body bounds, volume and face count; matching deterministic snapshots provide additional visual evidence. This qualifies the workflow mechanics without claiming that a non-AI test can measure the quality of every future semantic translation.

## Local startup and diagnostics

The installed `forge-cad-mcp` command remains the single server entrypoint. It accepts an optional positional mode (`serve`, default, or `doctor`) plus explicit workspace, Forge checkout and SolidCraft CLI paths. Explicit arguments are copied into the process-local configuration before any tool executes; environment variables remain fallback configuration. This keeps client configuration self-contained without changing library APIs.

The SolidCraft adapter stores one configured CLI executable instead of assuming PATH. `detect_version()` runs only `<cli> --version`; model/runtime methods still enforce the local-stdio execution gate and exact 0.49.0 version before CAD work.

`doctor` is deliberately not a CAD action. It checks the workspace contract, validates installed scpf 0.25.0 plus the exact clean Forge release checkout, and probes SolidCraft version. It returns structured JSON and a process status. The MCP `environment` tool returns the same readiness data without absolute paths. FastMCP is pinned to the exact 2.14.7 version qualified by protocol/runtime acceptance.

No VS Code/Claude/Codex-specific adapter exists. Their configuration points to the same stdio executable with the same arguments.

## Explicit CAD library and model binding

Normal catalog work uses two roots: `CAD_LIBRARY_ROOT` identifies the concrete checked-out CAD/model catalog and `CAD_MODEL_ROOT` identifies exactly one owner folder inside it. The CLI exposes these as `--cad-library` and `--model-root`; model-root may be a relative path such as `models/assemblies/simple_mft_assembly`. The server rejects missing directories, symlinks, paths outside `models/`, directories without `model.yml`, and paths outside the catalog.

When this binding is active, the selected model folder becomes the workspace root used by every source, build and runtime tool. `workspace_status` and MCP `environment` expose only the configured model ID and library-relative path so the AI knows the target without discovering one. Local `doctor` additionally includes absolute paths for diagnosis. MCP server instructions and both authoring skills forbid fuzzy target selection or implicit owner switching. The legacy `--workspace` path remains for deliberately standalone work only.

## Read-only catalog dependencies

The target owner remains the only workspace and the only writable boundary. Assemblies and subassemblies can inspect reusable owners elsewhere in the same configured CAD library through `catalog_dependency_list(owner)` and `catalog_dependency_read(owner, path)`. Both calls require exact catalog-relative paths; `catalog_dependency_list` accepts only a directory containing its own `model.yml`, and neither tool offers fuzzy search across the catalog. Native `.sc` dependencies remain opaque and are not exposed as text.

Forge compilation keeps its source and outputs inside the target owner. Forge 0.25's own model import context detects the enclosing `models/` tree and makes the project root available for existing namespace imports such as `from models.components.simple_mft...`; MCP does not add a parallel import mechanism. Dependency owners remain read-only through MCP. Target selection and dependency resolution are therefore separate concerns: one exact writable target, many exact read-only dependencies.

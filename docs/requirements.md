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

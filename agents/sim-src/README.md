# Sim shadow exports

`agent.tmpl` renders Sim 0.9.33 workflow JSON from each Dify-home definition selecting the Sim shadow.
The native Start and API blocks send one LiteLLM chat completion with the shared prefix and agent prompt.
Source triggers are retained as replay metadata; eligible graphs have no integration bindings or output sinks.

Configure the `LITELLM_API_BASE` workspace environment variable and each agent's `<AGENT_NAME>_LITELLM_API_KEY`
variable before import. Agent names are uppercased with hyphens replaced by underscores. The base ends in `/v1`.
The request carries agent, tier, privacy class, and shadow mode metadata. Model and accelerator attribution come from
the router's configured tracing. Langfuse/Phoenix trace delivery requires runtime acceptance.

`shared.tmpl` provides common shadow metadata and the chat request for both runtime templates. Prompt loading reuses
the Dify template's named `prompt` template. `agent_tools` preserves the full definition tool list for shadow review;
`omitted_tools` identifies definition tools that the shadow runtime does not bind. The runtime `tools` list contains
only the LiteLLM chat request. Sim and Langflow do not receive MCP or connector bindings, regardless of the source
tool names, and every selected Dify-home definition renders as a shadow replay.

Import format and native block references, accessed 2026-11-06:

- [Workflow import](https://docs.sim.ai/api-reference/workflows/importWorkflow)
- [Native API block](https://docs.sim.ai/workflows/blocks/api)
- [Pinned import/export implementation](https://github.com/simstudioai/sim/blob/v0.9.33/apps/sim/lib/workflows/operations/import-export.ts)
- [Pinned API block](https://github.com/simstudioai/sim/blob/v0.9.33/apps/sim/blocks/blocks/api.ts)
- [Native MCP access policies and argument limitations](https://docs.sim.ai/agents/mcp)
- [Pinned MCP operation arguments](https://github.com/simstudioai/sim/blob/v0.9.33/apps/sim/tools/mcp/run-operation.ts)

`make render-sim render-langflow` updates the exports. `make check-sim check-langflow` compares committed exports
with fresh renders and rejects source drift, changed exports, missing files, and orphan exports.

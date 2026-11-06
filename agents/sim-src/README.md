# Sim shadow exports

`agent.tmpl` renders Sim 0.9.33 workflow JSON from each Dify-home definition selecting the Sim shadow.
The native Start and API blocks send one LiteLLM chat completion with the shared prefix and agent prompt.
Source triggers are retained as replay metadata; eligible graphs have no integration bindings or output sinks.

Configure the `LITELLM_API_BASE` workspace environment variable and each agent's `<AGENT_NAME>_LITELLM_API_KEY`
variable before import. Agent names are uppercased with hyphens replaced by underscores. The base ends in `/v1`.
The request carries agent, tier, privacy class, and shadow mode metadata. Model and accelerator attribution come from
the router's configured tracing. Langfuse/Phoenix trace delivery requires runtime acceptance.

`shared.tmpl` provides the common shadow metadata and chat request for both runtime templates. Prompt loading reuses
the Dify template's named `prompt` template. Write, connector, and unknown tools are listed in `omitted_tools`.
Read-only tools are never silently omitted: eligibility is computed from each definition before rendering.
The check targets print each skipped agent and its unbound read-only tools. Definitions with mapped read tools are
also skipped until a read-only shadow identity has gateway grants.

Sim's native MCP access policy restricts exact operation names, but does not inspect arguments. The definition
contract used by Dify binds the tool namespace and passes the operation as an argument (`subcommand` for task tools).
Selecting that namespace therefore permits write subcommands too. Sim skips these agents with a source-linked
reason. Langflow likewise skips agents requiring MCP tools with the reason `Langflow MCP binding is not read-only`.
Agents without read-tool requirements render normally; eligibility is recalculated on every render.

Import format and native block references, accessed 2026-11-06:

- [Workflow import](https://docs.sim.ai/api-reference/workflows/importWorkflow)
- [Native API block](https://docs.sim.ai/workflows/blocks/api)
- [Pinned import/export implementation](https://github.com/simstudioai/sim/blob/v0.9.33/apps/sim/lib/workflows/operations/import-export.ts)
- [Pinned API block](https://github.com/simstudioai/sim/blob/v0.9.33/apps/sim/blocks/blocks/api.ts)
- [Native MCP access policies and argument limitations](https://docs.sim.ai/agents/mcp)
- [Pinned MCP operation arguments](https://github.com/simstudioai/sim/blob/v0.9.33/apps/sim/tools/mcp/run-operation.ts)

`make render-sim render-langflow` updates the exports. `make check-sim check-langflow` compares committed exports
with fresh renders and rejects source drift, changed exports, missing files, and orphan exports.

# Langflow export sources

`agent.tmpl` renders Langflow 1.13.0 flow JSON with the built-in TextInput and OpenAI extension components.
`text-input.json` is the TextInput entry from the release's component index; `openai.py` is the release's unmodified
OpenAI component source. Langflow flow JSON embeds native component source as part of its import format.

Upstream source, accessed 2026-11-06:

- [Import and export flows](https://docs.langflow.org/concepts-flows-import)
- [Component index](https://github.com/langflow-ai/langflow/blob/v1.13.0/src/lfx/src/lfx/_assets/component_index.json)
- [OpenAI component](https://github.com/langflow-ai/langflow/blob/v1.13.0/src/bundles/openai/src/lfx_openai/components/openai/openai_chat_model.py)
- [MIT license](https://github.com/langflow-ai/langflow/blob/v1.13.0/LICENSE)

Configure the `LITELLM_API_BASE` global variable and each agent's `<AGENT_NAME>_LITELLM_API_KEY` global variable
in the importing workspace. Agent names are uppercased with hyphens replaced by underscores. The base ends in `/v1`.
The flow consumes replay text through TextInput and terminates at the model response. It has no chat history or
integration output component. Source trigger declarations and omitted integration tools are retained in `data.metadata`;
triggers are replay descriptors and do not activate subscriptions or schedules.

Trace delivery uses the runtime and router's configured Langfuse/Phoenix tracing. Import, execution, routing policy,
and trace receipt require runtime acceptance separately from offline render checks.

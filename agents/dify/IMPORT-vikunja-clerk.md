---
type: Dify agent import guide
title: vikunja-clerk
description: Import and configure the code-guarded Vikunja task clerk.
tags: [dify, agent, vikunja, import]
timestamp: "2026-11-01T23:50:24Z"
---

## Import steps

Target: Dify 1.16.1 with App DSL 0.1.5.

1. Install the OpenAI-API-compatible model provider. Configure its API Base URL and key in the Dify workspace, then
   add a chat model named `small` for the router's `small` role.
2. Configure the `vikunja` MCP provider. Replace `VIKUNJA_MCP_PROVIDER_ID` in [vikunja-clerk.dsl.yml](./vikunja-clerk.dsl.yml)
   with that provider's Dify workspace identifier.
3. Import [vikunja-clerk.dsl.yml](./vikunja-clerk.dsl.yml) as an Advanced Chat app. The model has no MCP tools; every
   `vikunja_task_crud` workflow tool node is downstream of an in-app Code guard. Pass `project_id` and, for updates,
   `task_id` through the structured Start inputs; never populate these write mandates from model-produced intent.
4. Resolve these policy refs in the platform's protected environment settings. Store project IDs only in Dify's
   environment values, never in this public repository:
   - `policy://vikunja-clerk/allowed-projects` → `VIKUNJA_ALLOWED_PROJECTS`, as a JSON array.
   - `policy://vikunja-clerk/denied-projects` → `VIKUNJA_DENIED_PROJECTS`, as a JSON array. Denied entries win if
     they also appear in the allowed array.
   - `policy://vikunja-clerk/inbox` → `VIKUNJA_INBOX_PROJECT_ID`, as one runtime project ID.
   Set `VIKUNJA_MODE=shadow` for preview-only writes. The Code guards refuse writes if policy values are missing or
   malformed.
5. Bind the LiteLLM MCP permission to this agent's virtual key. Update the key with the native LiteLLM API so its
   `object_permission.mcp_servers` contains only `vikunja`:

   ```sh
   curl -sS -X POST "<LITELLM_BASE_URL>/key/update" \
     -H "Authorization: Bearer <LITELLM_ADMIN_KEY>" \
     -H "Content-Type: application/json" \
     -d '{"key":"<AGENT_VIRTUAL_KEY>","object_permission":{"mcp_servers":["vikunja"]}}'
   ```

   Verify discovery with the agent key. The response must list the `vikunja` MCP tools:

   ```sh
   curl -i -sS -X POST "<LITELLM_BASE_URL>/v1/mcp/tools" \
     -H "Authorization: Bearer <AGENT_VIRTUAL_KEY>" \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc":"2.0","id":"<REQUEST_ID>","method":"tools/list","params":{}}'
   ```

   Repeat the same list request with a different agent or interactive virtual key whose effective permissions exclude
   `vikunja`; the response must not contain any Vikunja tools. Then call one listed tool with that other key and valid
   arguments; LiteLLM must deny the call:

   ```sh
   curl -i -sS -X POST "<LITELLM_BASE_URL>/v1/mcp/tools" \
     -H "Authorization: Bearer <OTHER_VIRTUAL_KEY>" \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc":"2.0","id":"<REQUEST_ID>","method":"tools/call","params":{"name":"<VIKUNJA_TOOL_NAME>","arguments":<VALID_TOOL_ARGUMENTS_OBJECT>}}'
   ```

   Ensure no team, agent, organization, access-group, or server grant makes `vikunja` available to the other key, and
   leave `allow_all_keys` disabled. LiteLLM intersects permission levels; an empty or missing key list can inherit
   access, so it is not proof of denial. See the
   [LiteLLM MCP permission guide](https://docs.litellm.ai/docs/mcp_control).
6. Compose `shared/homelab.md` before the `vikunja-clerk` prompt when the platform renders the production app.
7. Keep `VIKUNJA_MODE=shadow` until the in-app Code guards, per-key MCP allowlist, and project policy values are active
   and verified. Set `VIKUNJA_MODE=live` only when live writes are authorized.

## Unverified for Dify 1.16.1

- The MCP provider identifier, tool schema import, and Advanced Chat workflow binding were not tested in a live Dify workspace.
- The in-app Code guards, project policy values, LiteLLM per-key MCP allowlist and negative-key verification, `small`
  router role, and shared-prefix composition were not exercised in a live deployment.

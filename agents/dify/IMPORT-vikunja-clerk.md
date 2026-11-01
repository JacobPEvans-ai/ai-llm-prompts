---
type: Dify agent import guide
title: vikunja-clerk
description: Import and configure the code-guarded Vikunja task clerk.
tags: [dify, agent, vikunja, import]
timestamp: "2026-11-01T22:59:38Z"
---

## Import steps

Target: Dify 1.16.1 with App DSL 0.1.5.

1. Install the OpenAI-API-compatible model provider. Configure its API Base URL and key in the Dify workspace, then
   add a chat model named `small` for the router's `small` role.
2. Configure the `vikunja` MCP provider. Replace `VIKUNJA_MCP_PROVIDER_ID` in [vikunja-clerk.dsl.yml](./vikunja-clerk.dsl.yml)
   with that provider's Dify workspace identifier.
3. Import [vikunja-clerk.dsl.yml](./vikunja-clerk.dsl.yml) as an Advanced Chat app. The model has no MCP tools; every
   `vikunja_task_crud` workflow tool node is downstream of an in-app Code guard.
4. Resolve these policy refs in the platform's protected environment settings. Store project IDs only in Dify's
   environment values, never in this public repository:
   - `policy://vikunja-clerk/allowed-projects` → `VIKUNJA_ALLOWED_PROJECTS`, as a JSON array.
   - `policy://vikunja-clerk/denied-projects` → `VIKUNJA_DENIED_PROJECTS`, as a JSON array. Denied entries win if
     they also appear in the allowed array.
   - `policy://vikunja-clerk/inbox` → `VIKUNJA_INBOX_PROJECT_ID`, as one runtime project ID.
   Set `VIKUNJA_MODE=shadow` for preview-only writes. The Code guards refuse writes if policy values are missing or
   malformed.
5. In LiteLLM, put the `vikunja` MCP server in the per-key MCP allowlist for this agent's own virtual key only. No
   other virtual key may list that server. Anyone may call the agent app itself.
6. Compose `shared/homelab.md` before the `vikunja-clerk` prompt when the platform renders the production app.
7. Keep `VIKUNJA_MODE=shadow` until the in-app Code guards, per-key MCP allowlist, and project policy values are active
   and verified. Set `VIKUNJA_MODE=live` only when live writes are authorized.

## Unverified for Dify 1.16.1

- The MCP provider identifier, tool schema import, and Advanced Chat workflow binding were not tested in a live Dify workspace.
- The in-app Code guards, project policy values, LiteLLM per-key MCP allowlist, `small` router role, and shared-prefix
  composition were not exercised in a live deployment.

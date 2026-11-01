---
type: Dify agent import guide
title: vikunja-clerk
description: Import and configure the read-only vikunja-clerk agent.
tags: [dify, agent, vikunja, import]
timestamp: 2026-11-01T00:00:00Z
---

## Import steps

Target: Dify 1.16.1 with App DSL 0.1.5.

1. Install the OpenAI-API-compatible model provider. Configure its API Base URL and key in the Dify workspace, then
   add a chat model named `small` for the router's `small` role.
2. Configure the `vikunja` MCP provider through the code-guarded runtime. Use a read-scoped Vikunja credential and
   enforce the `vikunja` allowlist in code before dispatch: `vikunja_task_crud` operations `list` and `get` only.
   Deny every unknown tool or operation.
3. Replace `VIKUNJA_MCP_PROVIDER_ID` in [vikunja-clerk.dsl.yml](./vikunja-clerk.dsl.yml) with that provider's Dify
   workspace identifier. Do not bind the app directly to an unrestricted Vikunja MCP provider.
4. Import [vikunja-clerk.dsl.yml](./vikunja-clerk.dsl.yml) as an Agent app.
5. Compose `shared/homelab.md` before the `vikunja-clerk` prompt when the platform renders the production app. The DSL
   contains the agent prompt but does not include the shared prefix contents.
6. Publish only after the code guard and read-scoped credential are active.

## Unverified for Dify 1.16.1

- The MCP provider identifier, tool schema import, and Agent-app MCP binding were not tested in a live Dify workspace.
- The platform code path that enforces the allowlist before MCP dispatch was not exercised here; this app must not be
  published with a direct, unrestricted MCP binding.
- The `small` router role, provider credential scope, and shared-prefix composition were not tested in a live deployment.

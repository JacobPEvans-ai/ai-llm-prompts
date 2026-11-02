---
type: Dify workflow import guide
title: vikunja-triage
description: Import and configure the scheduled, policy-guarded Vikunja triage Workflow.
tags: [dify, workflow, vikunja, triage]
timestamp: "2026-11-01T00:00:00Z"
---

## Import and schedule

Target: Dify 1.16.1 or 1.18.0 with Workflow apps, Schedule Trigger support, and App DSL 0.7.0.

1. Configure the OpenAI-compatible provider and the `medium` LiteLLM role.
2. Configure the `vikunja` MCP provider and bind this app to the shared
   `agent-vikunja-clerk` identity key through `openbao://agent-key/vikunja-clerk`. Replace `VIKUNJA_MCP_PROVIDER_ID` in
   [vikunja-triage.dsl.yml](./vikunja-triage.dsl.yml) with its workspace identifier. Confirm the provider supports
   `list`, `update`, and `comment` operations.
3. Import [vikunja-triage.dsl.yml](./vikunja-triage.dsl.yml) as a **Workflow** app. Do not import it as a Chatflow. Keep
   the native Schedule Trigger at `*/10 * * * *` (every ten minutes, minute resolution). Scheduled inputs are `{}`; the
   workflow uses `sys.timestamp`.
4. Publish with `VIKUNJA_TRIAGE_MODE=shadow`.

## Protected environment values

Resolve project policy refs to JSON arrays of opaque IDs. Keep all values in protected Dify settings; do not add real IDs or names here.

| Policy ref | Dify environment variable |
| --- | --- |
| `policy://vikunja-triage/allowed-projects` | `VIKUNJA_TRIAGE_ALLOWED_PROJECTS` |
| `policy://vikunja-triage/readonly-projects` | `VIKUNJA_TRIAGE_READONLY_PROJECTS` |
| `policy://vikunja-triage/rank-only-projects` | `VIKUNJA_TRIAGE_RANK_ONLY_PROJECTS` |
| `policy://vikunja-triage/denied-projects` | `VIKUNJA_TRIAGE_DENIED_PROJECTS` |

Also configure `VIKUNJA_TRIAGE_MODE` (`shadow` by default), `OPENBAO_ADDR`, `OPENBAO_ROLE_ID`, `OPENBAO_SECRET_ID`,
`GITHUB_READ_TOKEN_PATH`, `GITHUB_API_BASE`, and `GITHUB_WEB_HOST` using `<APPROVED_VALUE>` placeholders until
provisioned. The AppRole is `agent-vikunja-clerk`; `GITHUB_READ_TOKEN_PATH` resolves `github-token/vikunja-clerk` and
must mint a short-lived public-read token. Never log or return the token. Configure both GitHub bases to the approved
public service endpoints.

The guard refuses malformed policy, an unfiltered list, and every project absent from the policy. It lists only
`allowed ∪ readonly`, subtracting denied IDs; deny wins even when an ID appears on another list. `rank-only` must be a
subset of `allowed` and permits only priority/label updates. Readonly projects permit reads only.

## Shadow trace and promotion

Check the Langfuse trace for the scheduled Workflow run. Confirm its output contains the intended action JSON,
`mode: shadow`, and `dispatch: false`, and that no Vikunja write tool ran. Verify the trace uses the internal privacy
route and contains no credential values.

Promote `VIKUNJA_TRIAGE_MODE` to `live` only after the complete `agents/evals/vikunja-triage.yaml` set passes the judges
gate and the guard/policy configuration is verified. Live mode dispatches only guarded priority/label updates, verified
evidence comments, and completion updates whose GitHub reader result is merged or closed.

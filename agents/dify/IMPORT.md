---
type: Dify workflow import guide
title: Dify workflow imports
description: Import, configure, and publish the code-simplifier and ci-fixer workflows.
tags: [dify, workflow, github, import]
timestamp: "2026-11-02T23:11:47Z"
---

## code-simplifier import and run

Target: Dify 1.16.1 with App DSL 0.7.0.

## Generated DSL source and synchronization

Each committed DSL in `agents/dify/` is generated from its `agents/<name>.yaml` definition, workflow templates in
`agents/dify-src/<name>/`, and prompt source paths declared in that YAML. The YAML supplies the Dify app name and
LiteLLM role, plus schedule, mode-default, and MCP fields where declared; the templates supply graph structure. The
renderer inserts the declared system prompt. Never copy a prompt into Dify or edit a committed DSL by hand. Edit the
agent YAML or canonical prompt (or the template for graph changes), run `python3 agents/dify-src/render.py`, and commit
all changed sources with the generated DSL. The CI check runs
`python3 agents/dify-src/render.py --check` and fails on any byte difference.

1. Install the OpenAI-API-compatible model provider. Configure its API Base URL and key in the Dify workspace,
   then configure the `litellm_role` declared in `agents/code-simplifier.yaml` (`medium`). The Dify model field takes
   the role name, not a model ID.
2. Import [code-simplifier.dsl.yml](./code-simplifier.dsl.yml) as a Workflow app.
3. Set these workflow environment variables in Dify: `OPENBAO_ADDR`, `OPENBAO_ROLE_ID`, `OPENBAO_SECRET_ID`,
   `GITHUB_API_BASE`, `GITHUB_TOKEN_MINT_PATH`, `GITHUB_TOKEN_READ_SET`, and `GITHUB_TOKEN_WRITE_SET`. Store
   `OPENBAO_ROLE_ID` and `OPENBAO_SECRET_ID` as secrets. Keep values out of this repository.
4. Publish the workflow.
5. Run it through the Dify [Workflow Run API](https://docs.dify.ai/en/api-reference/workflow-runs/run-workflow)
   at `<DIFY_BASE_URL>/v1/workflows/run`, with the app API key in the Bearer `Authorization` header. Pass the
   immutable Eval/Router Mandate as the `inputs` object. Use
   `response_mode: "blocking"` and a stable caller identifier in `user`.

   ```json
   {
     "inputs": {
       "repo": "dryvist/<repository>",
       "ref": "<branch>",
       "head_sha": "<40-character commit SHA>",
       "actor": "<GitHub actor>",
       "event": "pull_request",
       "strength": "<Eval/Router strength>",
       "mode": "shadow",
       "pr_number": 123
     },
     "response_mode": "blocking",
     "user": "<stable caller identifier>"
   }
   ```

   Agents run with `mode: "shadow"` by default. Shadow runs use `GITHUB_TOKEN_READ_SET`, make no GitHub writes,
   and return the proposed review JSON and mandate trace in the workflow result. `mode: "live"` is comment-only:
   it can submit a `COMMENT` review after the target is rechecked against the Mandate.

## code-simplifier: provider credential scope

1. The agent's router key is `agent-key/code-simplifier` from `agents/code-simplifier.yaml`.
   Dify sets model-provider credentials per workspace. This app uses the workspace key from step 1 unless the per-agent design question changes it.

## code-simplifier: enable Langfuse tracing

Do this before the first published run.

1. In the Dify console, open this app, select **Monitoring**, then **Tracing app performance**, then
   **configure**. Dify documents this at
   <https://docs.dify.ai/en/use-dify/monitor/integrations/integrate-langfuse>.
2. Enter the Public Key, Secret Key, and Host of the shared Langfuse project. Keep the values out of this
   file and out of Git. Read the two keys from the OpenBao KV v2 leaf named by the variable
   `DIFY_LANGFUSE_OPENBAO_PATH` in mount `secret`, fields `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`.
   Read the Host from the variable `DIFY_LANGFUSE_HOST`. Both variables come from the runtime secret store.
3. Save. The status on the same page must read started.
4. Acceptance check, after one test run of the published app: take the top-level `workflow_run_id` from the
   blocking response of that run's Workflow Run API call, documented at
   <https://docs.dify.ai/en/api-reference/workflow-runs/run-workflow>. A Langfuse trace with that id must exist.
   The router log line for this run's request shows the key alias that request used. Take the alias from that line.
   If the alias is not the one this app uses, stop before any promotion.

## Unverified for Dify 1.16.1

- Step 1's provider installation screen, model registration flow, and provider credential scope were not tested in a live workspace.
- Steps 2–5's Console labels, environment variable editor, publish flow, and Workflow Run API call were not checked in a Dify 1.16.1 workspace.
- The router's `medium` role, Mandate values, and deployment API routing were not exercised here.

## ci-fixer import and run

Target: Dify 1.16.1 with App DSL 0.7.0.

1. Install the OpenAI-API-compatible model provider. Configure its API Base URL and key in the Dify workspace,
   then configure the `litellm_role` declared in `agents/ci-fixer.yaml` (`medium`). The Dify model field takes the
   role name, not a model ID.
2. Import [ci-fixer.dsl.yml](./ci-fixer.dsl.yml) as a Workflow app.
3. Set these workflow environment variables in Dify: `OPENBAO_ADDR`, `OPENBAO_ROLE_ID`, `OPENBAO_SECRET_ID`,
   `GITHUB_API_BASE`, `GITHUB_TOKEN_MINT_PATH`, `GITHUB_TOKEN_READ_SET`, `GITHUB_TOKEN_WRITE_SET`, and
   `ENABLE_PUSH`. Store `OPENBAO_ROLE_ID` and `OPENBAO_SECRET_ID` as secrets. Keep `ENABLE_PUSH` set to `false`
   by default.
4. Publish the workflow.
5. Run it through the Dify [Workflow Run API](https://docs.dify.ai/en/api-reference/workflow-runs/run-workflow)
   at `<DIFY_BASE_URL>/v1/workflows/run`, with the app API key in the Bearer `Authorization` header. Pass the
   immutable Eval/Router Mandate as the `inputs` object. Use
   `response_mode: "blocking"` and a stable caller identifier in `user`.

   ```json
   {
     "inputs": {
       "repo": "dryvist/<repository>",
       "ref": "<branch>",
       "head_sha": "<40-character commit SHA>",
       "actor": "<GitHub actor>",
       "event": "check_run",
       "strength": "<Eval/Router strength>",
       "mode": "shadow",
       "check_run_id": 123
     },
     "response_mode": "blocking",
     "user": "<stable caller identifier>"
   }
   ```

   Agents run with `mode: "shadow"` by default. Shadow runs use `GITHUB_TOKEN_READ_SET`, make no GitHub writes,
   and return the proposed patch and mandate trace in the workflow result. Live mode requires `ENABLE_PUSH` to be
   exactly `true`; source writes remain fail-closed while log redaction is unavailable.

## ci-fixer: provider credential scope

1. The agent's router key is `agent-key/ci-fixer` from `agents/ci-fixer.yaml`.
   Dify sets model-provider credentials per workspace. This app uses the workspace key from step 1 unless the per-agent design question changes it.

## ci-fixer: enable Langfuse tracing

Do this before the first published run.

1. In the Dify console, open this app, select **Monitoring**, then **Tracing app performance**, then
   **configure**. Dify documents this at
   <https://docs.dify.ai/en/use-dify/monitor/integrations/integrate-langfuse>.
2. Enter the Public Key, Secret Key, and Host of the shared Langfuse project. Keep the values out of this
   file and out of Git. Read the two keys from the OpenBao KV v2 leaf named by the variable
   `DIFY_LANGFUSE_OPENBAO_PATH` in mount `secret`, fields `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`.
   Read the Host from the variable `DIFY_LANGFUSE_HOST`. Both variables come from the runtime secret store.
3. Save. The status on the same page must read started.
4. Acceptance check, after one test run of the published app: take the top-level `workflow_run_id` from the
   blocking response of that run's Workflow Run API call, documented at
   <https://docs.dify.ai/en/api-reference/workflow-runs/run-workflow>. A Langfuse trace with that id must exist.
   The router log line for this run's request shows the key alias that request used. Take the alias from that line.
   If the alias is not the one this app uses, stop before any promotion.

## ci-fixer unverified for Dify 1.16.1

- Step 1's provider installation screen, model registration flow, and provider credential scope were not tested in a
  live workspace.
- Steps 2–5's Console labels, environment variable editor, publish flow, and Workflow Run API call were not checked
  in a Dify 1.16.1 workspace.
- The workflow's check_run input mapping, HTTP response fields, model provider binding, and check-run-to-PR association
  were not exercised in a Dify 1.16.1 workspace.
- No log-redaction service is connected; source writes remain blocked by code guards, and live GitHub behavior is
  unverified.

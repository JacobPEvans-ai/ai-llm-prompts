---
type: Dify agent import guide
title: docs-updater
description: Import and configure the shadow-only merged pull request documentation proposer.
tags: [dify, agent, github, documentation, import]
timestamp: "2026-11-06T20:00:00Z"
---

## Import steps

Target: Dify 1.16.1 with App DSL 0.7.0.

The app DSL is generated from `agents/docs-updater.yaml`, its declared prompts, and the shared gomplate template.
Edit the YAML's `dify` mapping for graph changes, then run `make render-dify` and commit the generated DSL.
See [generation, synchronization, and Dify 1.18 imports](./IMPORT.md) for the shared workflow and drift check.

1. Install the OpenAI-API-compatible model provider, configure its API Base URL and key in the Dify workspace, and add
   the medium chat model used by the agent.
2. Import docs-updater.dsl.yml as a Workflow app.
3. Set OPENBAO_ADDR, OPENBAO_ROLE_ID, OPENBAO_SECRET_ID, GITHUB_API_BASE, GITHUB_TOKEN_MINT_PATH, and
   GITHUB_TOKEN_READ_SET in the workflow environment. Store the AppRole values as secrets. Use the read-only set
   referenced by github-token/docs-updater; do not configure a GitHub write set. GITHUB_TOKEN_MINT_PATH must begin
   with a slash, because the workflow appends it to OPENBAO_ADDR.
4. Have the event router start the workflow only for pull_request closed events with merged true in the dryvist org.
   Pass the immutable repo and pr_number mandate, event metadata, and private_documentation_context as a JSON array
   of available pages with page_path and text fields.
5. Keep the agent in shadow mode. The workflow returns only safe structured proposals for run-record storage and has
   no documentation write operation. The docs_private.pull_request live channel remains off until the
   agent-docs-updater identity receives its required docs-private write grant.

## Provider credential scope

1. The agent's router key is `agent-key/docs-updater` from `agents/docs-updater.yaml`.
   Dify sets model-provider credentials per workspace. Expected: the workspace key from step 1. Open design
   question: per-agent keys, tracked in the ai-llm-prompts #249 gate.

## Enable Langfuse tracing

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
   <https://docs.dify.ai/en/api-reference/workflow-runs/run-workflow>. A Langfuse trace with that id must exist
   (inferred from Dify's Langfuse field table, which maps workflow_app_log_id/workflow_run_id to the id column;
   confirm at first import, and if the trace id differs, match on the run id in trace metadata instead). The
   router log line for this run's request shows the key alias it used. The expected alias is the workspace key
   alias named in step 1. Stop before any promotion if the log line shows a different alias.

## Unverified for Dify 1.16.1

- The provider setup, workflow environment editor, event-router field mapping, publish flow, and Workflow Run API
  call were not exercised in a live Dify workspace.

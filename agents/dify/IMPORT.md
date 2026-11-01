---
type: Dify workflow import guide
title: Dify workflow imports
description: Import, configure, and publish the code-simplifier and ci-fixer workflows.
tags: [dify, workflow, github, import]
timestamp: 2026-11-01T22:32:19Z
---

## Import steps

Target: Dify 1.16.1 with App DSL 0.7.0.

1. Install the OpenAI-API-compatible model provider. Configure its API Base URL and key in the Dify workspace,
   then add a chat model named `medium` for the router's `medium` role.
2. Import [code-simplifier.dsl.yml](./code-simplifier.dsl.yml) as a Workflow app.
3. Set these workflow environment variables in Dify: `OPENBAO_ADDR`, `OPENBAO_ROLE_ID`, `OPENBAO_SECRET_ID`,
   `GITHUB_API_BASE`, `GITHUB_TOKEN_MINT_PATH`, and `SHARED_PREFIX`. Store `OPENBAO_ROLE_ID` and
   `OPENBAO_SECRET_ID` as secrets. Keep values out of this repository.
4. Publish the workflow.
5. Copy the Webhook Trigger URL into the GitHub webhook relay route. Keep the URL reachable only from the relay.
   The relay must verify `X-Hub-Signature-256` against the original request body, deduplicate `X-Hub-Delivery`,
   forward `X-GitHub-Event`, `X-Hub-Delivery`, and the JSON payload, and set
   `X-Relay-Signature-Verified: true` only after signature verification succeeds.

## Unverified for Dify 1.16.1

- Step 1's provider installation screen, model registration flow, and provider credential scope were not tested in a live workspace.
- Steps 2–5's Console labels, environment variable editor, publish flow, and Webhook Trigger URL location were not checked in a Dify 1.16.1 workspace.
- The router's `medium` role and the relay's routing and deduplication behavior depend on the target deployment and were not exercised here.

## ci-fixer import steps

Target: Dify 1.16.1 with App DSL 0.7.0.

1. Install the OpenAI-API-compatible model provider. Configure its API Base URL and key in the Dify workspace,
   then add a chat model named `medium` for the router's `medium` role.
2. Import [ci-fixer.dsl.yml](./ci-fixer.dsl.yml) as a Workflow app.
3. Set these workflow environment variables in Dify: `OPENBAO_ADDR`, `OPENBAO_ROLE_ID`, `OPENBAO_SECRET_ID`,
   `GITHUB_API_BASE`, `GITHUB_TOKEN_MINT_PATH`, `SHARED_PREFIX`, and `ENABLE_PUSH`. Store `OPENBAO_ROLE_ID` and
   `OPENBAO_SECRET_ID` as secrets. Keep `ENABLE_PUSH` set to `false`; source writes are code-disabled until an
   approved log-redaction service is wired in and the workflow guard is explicitly updated.
4. Publish the workflow.
5. Copy the Webhook Trigger URL into the GitHub webhook relay route for `check_run` events. The relay must verify
   `X-Hub-Signature-256` against the original request body, deduplicate `X-Hub-Delivery`, forward
   `X-GitHub-Event`, `X-Hub-Delivery`, and the JSON payload, and set `X-Relay-Signature-Verified: true` only after
   signature verification succeeds.

## ci-fixer unverified for Dify 1.16.1

- Step 1's provider installation screen, model registration flow, and provider credential scope were not tested in a live workspace.
- Steps 2–5's Console labels, environment variable editor, publish flow, and Webhook Trigger URL location were not checked in a Dify 1.16.1 workspace.
- The workflow's check_run input mapping, HTTP response fields, model provider binding, and webhook relay routing were not exercised in a Dify 1.16.1 workspace.
- No log-redaction service is connected; model and Git Data writes remain blocked by code guards, and live GitHub behavior is unverified.

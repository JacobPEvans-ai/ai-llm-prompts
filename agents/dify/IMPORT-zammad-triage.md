---
type: Dify workflow import guide
title: zammad-triage
description: Import and configure the scheduled, policy-guarded Zammad triage Workflow.
tags: [dify, workflow, zammad, triage]
timestamp: "2026-11-02T00:00:00Z"
---

## Import and schedule

Target: Dify 1.16.1 or 1.18.0 with Workflow apps, Schedule Trigger support, and App DSL 0.7.0.

1. Configure the OpenAI-compatible provider and the medium LiteLLM role. Its router key must be scoped to local-only
   models; cloud fallback is forbidden.
2. Bind this app to the agent-zammad-triage identity key through openbao://agent-key/zammad-triage. Import
   [zammad-triage.dsl.yml](./zammad-triage.dsl.yml) as a **Workflow** app, not a Chatflow.
3. Keep the native Schedule Trigger at a ten-minute cadence (minute resolution). Scheduled inputs are {};
   the workflow uses sys.timestamp. Publish with ZAMMAD_TRIAGE_MODE=shadow.

## Protected environment values

Resolve policy refs to JSON arrays of opaque group ID strings. Keep values in protected Dify settings. Include all client
and business group IDs in the denied array; the guard rejects tickets outside its computed scope even if search returns
them.

| Policy ref | Dify environment variable |
| --- | --- |
| policy://zammad-triage/allowed-groups | ZAMMAD_TRIAGE_ALLOWED_GROUPS |
| policy://zammad-triage/readonly-groups | ZAMMAD_TRIAGE_READONLY_GROUPS |
| policy://zammad-triage/denied-groups | ZAMMAD_TRIAGE_DENIED_GROUPS |

Also configure ZAMMAD_TRIAGE_TAG_VOCABULARY as a JSON array, ZAMMAD_TRIAGE_MODE (shadow by default), OPENBAO_ADDR,
OPENBAO_ROLE_ID, OPENBAO_SECRET_ID, ZAMMAD_TOKEN_PATH, and ZAMMAD_API_BASE with approved values. Leave the API base
empty until provisioned. The AppRole is agent-zammad-triage; the token path resolves the Zammad API token. The request
header is Authorization: Token token= followed by the fetched token. The token stays inside the two code nodes that
call Zammad and is never a workflow variable, log line, or output.

The search node refuses malformed group policy and an empty read scope. It searches each group in
allowed ∪ readonly, subtracting denied IDs. Deny wins, and readonly groups permit reads only. Malformed policy denies
all reads and writes. Every HTTP request rejects redirects.

## Shadow trace and promotion

Check the Langfuse trace for the scheduled Workflow run. Confirm its output contains the intended action JSON,
mode: shadow, and an empty results array, and that no Zammad write request ran. Verify the model received only ticket index,
title, priority, state name, age, tags, and last-updated age, with no customer fields or article bodies.

Set ZAMMAD_TRIAGE_MODE to live only after the complete agents/evals/zammad-triage.yaml set passes the judges gate and
the guard and policy configuration are verified. Live mode dispatches only guarded priority updates, vocabulary tags,
and fixed internal notes. Incident proposals remain output only in both modes.

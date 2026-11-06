---
type: Dify workflow import guide
title: Model-only text agents
description: Import and call the style-gate, plain-rewriter, tag-suggester, commit-grouper, and action-extractor Workflows.
tags: [dify, workflow, agent, import]
timestamp: "2026-11-06T20:00:00Z"
---

## Agents

Each agent is a Workflow app with one model call and no tools. It reads one `text` input and returns one envelope.

| Agent | Input `text` | Result |
| --- | --- | --- |
| `style-gate` | One Markdown draft, or a JSON object whose string values are checked | `{pass, findings}` |
| `plain-rewriter` | One Markdown draft | `{text, changes}` |
| `tag-suggester` | JSON with `allowed_tags`, `path`, and `excerpt` | `{tags}` |
| `commit-grouper` | JSON with `allowed_prefixes` and `changes` (`git status --porcelain -u` output) | `{groups}` |
| `action-extractor` | Notes or conversation text, with an optional `MY NOTES` section | `{summary, action_items}` |

## Generated DSL source and synchronization

Each DSL is generated from `agents/<name>.yaml`, its declared prompts, and the shared gomplate template.
The template embeds `output_schema` in the `Validate reply` Code node. Edit the YAML's `dify` mapping for graph
changes, then run `make render-dify` and commit the generated DSL.
See [generation, synchronization, and Dify 1.18 imports](./IMPORT.md) for the shared workflow and drift check.

## Import steps

Target: Dify 1.16.1 or later with Workflow apps and App DSL 0.7.0.

1. Configure the OpenAI-compatible provider and the `litellm_role` declared in each YAML (`medium`). Each agent's
   router key is `openbao://agent-key/<name>`.
2. Import `agents/dify/<name>.dsl.yml` as a **Workflow** app, then publish it.
3. Call it through the Dify Workflow Run API at `<DIFY_BASE_URL>/v1/workflows/run`, with the app API key in the
   Bearer `Authorization` header:

   ```json
   {"inputs": {"text": "<input>"}, "response_mode": "blocking", "user": "<stable caller identifier>"}
   ```

## Output

The workflow returns `status` and `envelope`. `envelope` is a JSON string of
`{"status": "ok" | "refused" | "stop", "reason": "...", "result": ...}` that matches the agent's `output_schema`.
The `Validate reply` node turns any reply that fails the schema or the agent rule named in its YAML into
`status: stop` with a null `result`. Empty input always returns `stop`.

## Unverified

- These workflows were not imported into a live Dify workspace.

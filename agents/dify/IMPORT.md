---
type: Dify workflow import guide
title: Dify workflow imports
description: Generate, import, validate, and export published Dify workflows with difyctl.
tags: [dify, workflow, import, difyctl]
timestamp: "2026-11-06T20:00:00Z"
---

## Generated DSL source and synchronization

`agents/<name>.yaml` and its declared prompt sources are the inputs to 1 shared template,
`agents/dify-src/agent.tmpl`. The maintained [gomplate renderer](https://docs.gomplate.ca/) supplies YAML parsing,
file loading, parameter substitution, and serialization. The flake lock pins its package through nixpkgs.
The dev shell provides the renderer, Make, YAML tools, and agent test dependencies.

```sh
nix develop --command make render-dify
nix develop --command make check-dify
nix develop --command python3 -m pytest -q agents/judges
```

`render-dify` selects every definition with `home_platform: dify`; other homes are excluded. New definitions use
the standard Start → model → End workflow without a fragment directory. A definition's optional `dify` mapping
supplies its existing workflow graph, including node settings and Code-node source. Parameters and canonical
prompts are inserted as data. Prompt text and Code-node source are never evaluated as gomplate templates.
Scheduled graphs use `triggers[].cadence` directly; `skew_minutes` is already included in that cadence.

Edit the YAML, canonical prompt, or shared template, and commit the generated DSL with it. Keep the generated-file
header. `check-dify` renders into a temporary directory and compares the complete output set byte for byte,
including headers. CI rejects changed content, missing outputs, and extra outputs. Graph overrides retain the
existing workflows' behavior; a new definition can render without one.

To render another checkout's agent definitions and prompts with this checkout's template and helpers:

```sh
make render-dify AGENTS_ROOT=/path/to/checkout DIFY_OUTPUT=/path/to/output
```

## Dify 1.18 compatibility

| Artifact | Contract |
| --- | --- |
| Committed `.dsl.yml` | App DSL 0.7.0, or 0.1.5 for `vikunja-clerk`; generated YAML retained for import |
| Dify application and difyctl | Matching 1.18.0 versions; use the server's operation catalog |
| Portable `.ifpkg` package | Separate export/import acceptance check on Dify 1.18.0 or later |
| Agent Backend and sandbox | Match the application release and retain the published build snapshot and skill versions |

Dify 1.18 supports YAML and portable packages. Keep package round-trip validation separate from generated YAML
parity. Match the Agent Backend, runtime, and sandbox components when using Agent nodes. These are application
compatibility requirements; this repository's offline checks do not prove a successful import.
[Dify 1.18 release](https://github.com/langgenius/dify/releases/tag/1.18.0).

## Import and test with difyctl

1. Use the matching difyctl client. Authenticate through the approved runtime login flow, then discover the
   connected server's commands:

   ```sh
   difyctl login --server "$DIFY_BASE_URL"
   difyctl help
   ```

2. Use the discovered app and Workflow operations to import `agents/dify/<name>.dsl.yml` into a draft.
   Inspect command help for input fields and the current draft hash before updating an existing app.
3. Configure the definition's model-provider role, environment variables, and resource bindings in the destination
   workspace. Keep credential values in the approved runtime store. Configure trace delivery before test runs.
4. Run the draft with the agent's evaluation fixtures and validate its output contract. Exercise configured branches,
   missing tools, failure handling, and pause/resume where present. Confirm intended trigger bindings.
5. Record the rollback version, publish the tested draft, and run the published version. Verify resource bindings,
   active trigger subscriptions, and trace receipt in Langfuse and Phoenix. Confirm the run metadata includes
   `agent`, `tier`, `privacy_class`, `model`, and `accelerator`.

Dify 1.18 discovers authoring, import/export, publish, and execution operations from the server. Use their current
help instead of retaining an older hard-coded run route. Its client requires a fresh login when moving from v1.
[Dify 1.18 CLI contract](https://github.com/langgenius/dify/releases/tag/1.18.0).

## Export the published version

Select the intended published version in version history and export from that version's menu. Default Workflow,
Chatflow, and Agent exports contain the saved draft. Use the corresponding difyctl export operation only when its
discovered inputs explicitly select that published version. Otherwise use version history.

Leave **Export secret values** off. Version-history exports omit them. Review the artifact before storing or
sharing it. Record required integrations, knowledge bases, external tools, persistent Agent files, credentials,
and trigger subscriptions separately; configure these bindings again in the destination. Exports omit runtime
history and previous versions. Import the exported artifact into a test app, exercise the published fixtures,
and verify trace receipt before promotion. Keep generated YAML validation and package round-trip acceptance separate.
[Export and Import Apps](https://docs.dify.ai/en/self-host/use-dify/workspace/export-import-apps).

## Acceptance evidence

Record source generation, import, draft execution, publication, published execution, and trace receipt as separate
checks. The offline suite validates source parity and generation. Live Dify 1.18 import, execution, package
round-trip, trigger activation, and trace delivery remain unverified until tested in an authorized workspace.

---
type: Agent definition specification
description: Version 2 of the platform-neutral agent definition contract.
timestamp: 2026-11-09T20:40:34Z
---

# Agent definition schema v2

Definitions are YAML mappings at `agents/<name>.yaml`. The executable schema is
[`judges/test_agent_definitions.py`](judges/test_agent_definitions.py).
Agent-specific extension fields are preserved.

## Profiles and resolution

Each definition declares `extends: <profile>`, selecting `agents/profiles/<profile>.yaml`.
`agents/profiles/defaults.yaml` supplies shared values. Profiles contain only differences
from defaults; definitions contain only differences from their selected profile.
The resolver uses gomplate's native `coll.Merge` with definition values taking precedence over profile
values, and profile values over defaults. Mappings merge recursively; lists and scalars replace their inherited value.
Profiles are flat and cannot extend another profile. `defaults` is reserved.

`make resolve-agents` materializes the merged definitions for both Dify rendering and
pytest judges. It derives `prompt: agents/prompts/<name>.md` and
`eval_set: agents/evals/<name>.yaml`; neither field appears in source definitions or
profiles. `identity` and `api_key_ref` remain explicit in each definition.

## Overlay rosters

A downstream overlay copies its own definitions, prompts, evals, fixtures, rendered Dify DSLs and
manifests into a copy of this repository. The judges accept such a roster without deselection:

- Overlay definitions declare their own `extends` profile, with their own `shared_prefix`. Every definition's
  `shared_prefix` must equal the `shared_prefix` declared by a profile in its own `extends` chain, resolved through
  `agents/profiles/*.yaml`; an added overlay profile may declare its own prefix.
- Overlay Dify DSLs are covered by an additional `agents/dify/manifest.<roster>.json`. Each
  manifest covers only its own roster's DSLs, the manifests together name every roster DSL — each Dify-home
  agent and the rotation driver — and cover every rendered DSL exactly once, and every entry keeps the fields,
  sha256, mode, tier, and kind checks.
- Every eval suite with unskipped `expected_parse` cases also yields a `<agent>-parse` suite, scored against
  the "Parse request" system prompt of that agent's own rendered DSL.

## Fields

The following requirements apply to the merged definition unless marked source-only.

| Field | Type | Contract |
| --- | --- | --- |
| `extends` | string | Source-only profile name; letters, digits and hyphens. |
| `name` | string | Required; matches the filename, uses lowercase letters, digits and hyphens; excludes `fill` and `-vN` segments. |
| `description` | string | Required; nonempty `Use when:` and `Do not use when:` lines, trigger scenarios and a prompt invocation pointer. |
| `owner` | string | Required accountable owner. |
| `tier` | integer | Required: `0` interactive, `1` event-driven, or `2` batch. |
| `home_platform` | enum | Required: `dify`, `hermes`, `sim`, `langflow`, or `litellm`. |
| `shadows` | list[string] | Required platform names; unique and excluding the home. |
| `privacy_class` | enum | `public`, `internal`, or `private`; omission means `private`. |
| `triggers` | list[object] | Required, non-empty; replaces singular `trigger`. |
| `connectors` | list[string] | Required, unique connector agent names called through A2A; excludes this agent's name. |
| `kind` | enum | `agent` by default, or `connector`. |
| `owns` | string | Integration name; only `kind: connector` may declare it. Each declared integration has one owner. |
| `code_work` | enum | Required: `none` or `sandbox`. Agents editing code declare `sandbox`. |
| `mode` | enum | Required: `shadow` or `live`. |
| `eval_set`, `prompt` | paths | Derived from `name`; existing eval and OKF prompt files. |
| `shared_prefix` | path | Required existing OKF prompt file; declared by a profile in the definition's `extends` chain. |
| `tools`, `mcp_servers` | list[string] | With `mcp_servers`, `prefix.name` names tool `name` if `prefix` is listed, else (not `a2a.*`) a subcommand. |
| `litellm_role` | string | Required router role. |
| `memory_scope` | string | Required per-agent memory boundary, or `none`. |
| `identity`, `api_key_ref` | string | Explicit, non-empty runtime identity and credential reference; never inherited or derived. |
| `eval_policy` | object | Merged acceptance thresholds and baseline comparison rule. |
| `delivery` | object | Optional Slack thread digest for Dify agents; see [Delivery](#delivery). |

Tool and server lists hold unique strings, and empty lists are permitted. Any other dotted entry except `a2a.*` keeps
the subcommand form: tool `prefix` on the first MCP server, called with subcommand `name`. An entry without a dot
names a tool of that name on the first MCP server. Without `mcp_servers`, no entry is an MCP tool.

## Triggers

Each trigger declares one of these kinds:

| Kind | Fields | Meaning |
| --- | --- | --- |
| `rotation` | `every: <positive integer><m\|h\|d>`, optional `minute` | Minimum interval, meaning "not more often than"; tier 0/1 native, tier 2 driver. |
| `anchor` | `at: "HH:MM"`, optional `days: [Mon, ..., Sun]` | Fixed UTC time, daily when days is omitted; odd minute excluding `:15` and `:45`. |
| `event` | `source: <integration>` | An integration webhook, with optional event filters. |
| `call` | `source: <caller>` | Explicit invocation through the gateway. |

Raw `cron` and `cadence` fields are forbidden outside rendered Dify graph data.
The renderer owns schedule expressions. Tier 2 rotation agents expose a webhook entry for
driver calls; tracker events share that entry. The shared driver owns their windows
and live pace controls. The driver's Dify app name is the `ROTATION_DRIVER_NAME` make variable,
3 to 63 lowercase letters, digits, or hyphens (default `tier2-rotation`), so an overlay can
render its own driver beside the public one. Tier 0/1 rotations use native schedules; supported
intervals are minute divisors of 60 of at least two minutes, hour divisors of 24, and one day.
Native minute schedules omit `:00`, `:15`, `:30`, and `:45` from their compiled
minute lists. Omitted starts wait for the next scheduled minute, preserving the
minimum interval; `every: 15m` starts at `:07`, `:22`, `:37`, and `:52`.
Anchors render a native Dify schedule in UTC. Tracker triage uses its webhook plus a rotation catch-up.
`minute` is valid only with `every: 1h`, and `every: 1h` requires it. The value must be an odd minute
from 1 to 59, excluding 15 and 45. Native schedules fire at that minute; tier 2 agents offset to it, so
hourly tier 2 agents must not share a minute.
Start nodes and trigger nodes remain mutually exclusive within a Dify workflow.

```yaml
triggers:
  - kind: event
    source: vikunja
  - kind: rotation
    every: 1d
```

## Delivery

`delivery` sends a Dify agent's final output to Slack. Its keys are `kind: slack_thread`, `thread: daily_parent`,
`channel_env`, `token_env`, `failure_channel_env`, `dashboard_url_env`, `max_chars` (100 to 10000), and
`input_from: [<node>, <output>]`. `error_from: [<node>, <output>]` is optional. Unknown keys fail the render. The four
env names must be distinct, and the failure channel env must differ from the delivery channel env.

The renderer adds a Code node before each end node. At run time it takes one of three states:

- Fetch failed (`error_from` is not empty): one notice to the failure channel, then the run fails.
- Nothing fetched (the value at `input_from` is an empty list, object, or string): no post, and the run succeeds.
- Fetched: one reply in the agent's parent thread for the UTC day, cut to `max_chars` with a `[truncated]` marker.

Every failed post or history read sends one notice and then fails the run. An agent sends at most one notice per 24
hours: when the failure channel already holds one from it in that window, no notice is posted and the run still
fails. Each end node reports `delivery_status`.
Text is redacted, then escaped (`&`, `<`, `>`), so model or task text cannot mention, link, or broadcast. Channels must
be Slack channel IDs (`^[CGD][A-Z0-9]+$`), and the API base must be `https` on `slack.com`. The parent is found by its
exact text. The history cursor is followed to the end of the day, which starts at 00:00 UTC. Two starts in the same
second can both miss the parent and create two; that race remains.

Coverage gaps. Dify gives this pattern no hook for a failed `dispatch_write` in live mode. Such a failure fails the
iteration and the run, with no notice. Only the list call and its bind node route fetch errors. A model reply that
Guard verification errors are reported through `fetch_error`. A model reply that is not JSON, or not an object with an
`actions` array, is reported the same way. An action item that is not an object with an integer `task_index` and a known
`kind` is reported the same way.

The renderer also declares `SLACK_API_BASE`, which the deployment fills in.

## Standards gate

CI checks source definitions against their resolved profile and rejects equal inherited
leaf values, including inside partially overridden mappings. Lists replace atomically.
It also rejects identical normalized prompt bodies, equal name stems (hyphen and
underscore word separators normalize identically), and `-vN` name segments.
Semantic overlap between differently named jobs remains a reviewer judgment.

Every other roster agent named in a prompt body must be declared in `connectors`
or `peers`, with `a2a.call` in the resolved tools. This applies to all mentions,
including invocation examples. Reword references that do not call another agent.

New definitions summarize two to four representative trigger scenarios in their source
`description`. Their canonical prompts contain a `## When to invoke` section with
worked prose scenarios that connect supplied inputs to the permitted action.
Keep profile values inherited; invocation guidance belongs to each agent's definition
and prompt, and the renderer includes the prompt in every supported runtime.

Each eval case declares `category`. Every suite covers `normal`, `malformed`,
`ambiguous`, `oversized`, `unavailable-source`, and `negative-trigger`, with an input
and an expected result or behavior. Existing additional case categories are permitted.

`eval_policy.thresholds` defines correctness, privacy, latency, cost, and consequential
failure acceptance bounds. Defaults live once in the shared profile. The
`eval_policy.baseline` rule compares results against the previous released version;
missing baseline results block promotion. Overrides state only differing bounds.
These checks validate the evaluation contract; running model evaluations and comparing
released results remain separate promotion gates.

## Execution and checks

Dify is the live home, with Sim and Langflow shadows. Integration credentials belong
to connector agents; other agents call them through agentgateway. Code and test
execution belongs to agent-sandbox jobs.

Promotion from `shadow` to `live` requires passing promptfoo evals and 7 days of
shadow evidence without a Langfuse score regression. Runtime promotion and connector
deployment are separate from definition validation.

```sh
make test
```

---
type: Agent definition specification
description: Version 2 of the platform-neutral agent definition contract.
timestamp: 2026-11-06T00:00:00Z
---

# Agent definition schema v2

Definitions are YAML mappings at `agents/<name>.yaml`. The executable schema is
[`judges/test_agent_definitions.py`](judges/test_agent_definitions.py).
Agent-specific extension fields are preserved.

## Profiles and resolution

Each definition declares `extends: <profile>`, selecting `agents/profiles/<profile>.yaml`.
`agents/profiles/defaults.yaml` supplies shared values. Profiles contain only differences
from defaults; definitions contain only differences from their selected profile.
The resolver uses gomplate's native `coll.Merge` in precedence order: defaults, profile,
definition. Mappings merge recursively; lists and scalars replace their inherited value.
Profiles are flat and cannot extend another profile. `defaults` is reserved.

`make resolve-agents` materializes the merged definitions for both Dify rendering and
pytest judges. It derives `prompt: agents/prompts/<name>.md` and
`eval_set: agents/evals/<name>.yaml`; neither field appears in source definitions or
profiles. `identity` and `api_key_ref` remain explicit in each definition.

## Fields

The following requirements apply to the merged definition unless marked source-only.

| Field | Type | Contract |
| --- | --- | --- |
| `extends` | string | Source-only profile name; letters, digits and hyphens. |
| `name` | string | Required; matches the filename, uses lowercase letters, digits and hyphens; excludes `fill` and `-vN` segments. |
| `description` | string | Required; separate `Use when:` and `Do not use when:` lines with non-empty conditions. |
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
| `shared_prefix` | path | Required existing OKF prompt file; one shared prefix across the roster. |
| `tools`, `mcp_servers` | list[string] | Required unique tool and MCP names; empty lists are permitted. |
| `litellm_role` | string | Required router role. |
| `memory_scope` | string | Required per-agent memory boundary, or `none`. |
| `identity`, `api_key_ref` | string | Explicit, non-empty runtime identity and credential reference; never inherited or derived. |
| `eval_policy` | object | Merged acceptance thresholds and baseline comparison rule. |

## Triggers

Each trigger declares one of these kinds:

| Kind | Fields | Meaning |
| --- | --- | --- |
| `rotation` | `every: <positive integer><m\|h\|d>` | Minimum interval, meaning "not more often than"; evaluated by the shared rotation driver. |
| `anchor` | `at: "HH:MM"` | Fixed daily UTC time; odd minute excluding `:15` and `:45`. |
| `event` | `source: <integration>` | An integration webhook, with optional event filters. |
| `call` | `source: <caller>` | Explicit invocation through the gateway. |

Raw `cron` and `cadence` fields are forbidden outside rendered Dify graph data.
The renderer owns schedule expressions. Rotation agents expose a callable start;
the shared driver owns their windows and live pace controls. Anchors render a native
Dify daily schedule in UTC. Tracker triage uses its webhook plus a rotation catch-up.

```yaml
triggers:
  - kind: event
    source: vikunja
  - kind: rotation
    every: 1d
```

## Standards gate

CI checks source definitions against their resolved profile and rejects equal inherited
leaf values, including inside partially overridden mappings. Lists replace atomically.
It also rejects identical normalized prompt bodies, equal name stems (hyphen and
underscore word separators normalize identically), and `-vN` name segments.
Semantic overlap between differently named jobs remains a reviewer judgment.

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

---
type: Agent definition specification
description: Version 2 of the platform-neutral agent definition contract.
timestamp: 2026-11-06T00:00:00Z
---

# Agent definition schema v2

Definitions are YAML mappings at `agents/<name>.yaml`. The executable schema is
[`judges/test_agent_definitions.py`](judges/test_agent_definitions.py).
Agent-specific extension fields are preserved.

## Fields

| Field | Type | Contract |
| --- | --- | --- |
| `name` | string | Required; matches the filename, uses letters, digits and hyphens, and excludes `fill` regardless of case. |
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
| `eval_set` | path | Required non-empty path to an existing regression eval file. |
| `prompt`, `shared_prefix` | paths | Required existing prompt files with OKF metadata; one shared prefix across the roster. |
| `tools`, `mcp_servers` | list[string] | Required unique tool and MCP names; empty lists are permitted. |
| `litellm_role` | string | Required router role. |
| `memory_scope` | string | Required per-agent memory boundary, or `none`. |
| `identity` | string | Required unique runtime identity reference. |

## Triggers

Each trigger requires `kind: event|schedule|call`, a non-empty `source`, and an
integer `skew_minutes` from 0 through 59. Event filters and source selectors remain
extension fields on the corresponding trigger.

Only schedules declare `cadence`. It is numeric five-field cron, supporting lists,
ranges and positive steps. All expanded minute values exclude 0, 15, 30 and 45.
`cadence` contains the final start minutes; `skew_minutes` records the offset
already included in that cadence and is not added again by the renderer.

```yaml
triggers:
  - kind: schedule
    source: dify
    cadence: "2,12,22,32,42,52 * * * *"
    skew_minutes: 2
```

## Execution

The migrated definitions use Dify homes with Sim and Langflow shadows. Connector
names describe calls through agentgateway; integration credentials belong to the
named connector. Code and test execution belongs to agent-sandbox jobs.

Promotion from `shadow` to `live` requires passing promptfoo evals and 7 days of
shadow evidence without a Langfuse score regression. Runtime promotion and
connector deployment are separate from definition validation.

## Checks

```sh
pytest -q agents/judges
make check-dify
```

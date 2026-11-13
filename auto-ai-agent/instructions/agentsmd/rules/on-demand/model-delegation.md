---
name: model-delegation
description: CLI procedure for delegated work through Codex, with the routing order defined in AGENTS.md
type: LLM Prompt
title: "Model delegation"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/model-delegation"
tags:
  - shared-instructions
  - agent-instructions
timestamp: "2026-11-13T12:00:00Z"
status: active
consumers:
  - dryvist/nix-ai
  - dryvist/nix-claude-code
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-assistant-instructions
    path: "agentsmd/rules/on-demand/model-delegation.md"
    note: Migrated from the instruction repository.
---

# Model delegation

Routing order: [AGENTS.md](../../../AGENTS.md), "Delegation routing". Shared delegation doctrine: `prompt://dryvist/auto-ai-agent/model-delegation`.

Use configured Herdr by default for cross-agent and background agent work. Read the official Herdr skill
matching the selected server release and follow it. This rule authorizes targeting an explicitly configured
saved machine with `--machine`, or a configured `--remote` target, even when work started outside Herdr; this
authorization differs from the 0.9.5 skill's inside-pane-only condition for that target. Keep its other safety
checks; do not fabricate `HERDR_ENV`. Do not infer a target, start a local server, or silently change execution
location when the selected target is unavailable; report the failure.

If Herdr is not configured or available, state that and use the harness Agent tool as the fallback. Disclose
the fallback location; if it is not already authorized, ask before launching work there. Apply the same routing,
content eligibility, credential, read-only, and approval rules on either path; Herdr does not grant new authority.
Session start reports `codex-quota`. The routing order is in [AGENTS.md](../../../AGENTS.md), under "Delegation
routing"; this file covers CLI procedure only. Codex is eligible only while `codex-quota` exits 0.
The agent hook denies `codex exec` from a tool shell unless stdin comes from a prompt file.

When a runtime must call the Codex CLI directly (sandbox entrypoints or the router itself), pass the prompt as `-`
with finite stdin, or as a positional argument with stdin closed (`</dev/null`); always set `-o <file>`. Treat a
non-zero exit or empty final message as failure and surface it.

A delegate returns its result in the final message: one line (`STATUS|ITEM|REASON`) or a schema. Read-only delegates
never get a report-file contract. Background work is complete only after its result is retrieved and checked; a job ID
is not a result.

## When a Codex worker is blocked

Routed workers run `workspace-write` (`read-only` for Explore, Plan and advisory work), with no credential
store and no keychain. That is the default; keep it. A worker that hits a wall stops with
`BLOCKED|NEED <kind>|<detail>` and never works around it. The lead re-runs that step as a direct Codex run, widened
only for the named blocker:

```sh
( export GH_TOKEN="$(<mint a 1 h token for one repo; print only the token>)" GITHUB_TOKEN="$GH_TOKEN"
  codex exec -s workspace-write -C <worktree> --add-dir <path> \
    -c shell_environment_policy.ignore_default_excludes=true -o <out> - < <brief.md> )
```

| Blocker | Lead adds |
| --- | --- |
| Write outside the working directory (another repo, the scratchpad) | `-C <worktree>` and one `--add-dir` per directory |
| Git writes (`fetch`, `rebase`, `commit`, `push`) | Nothing: the sandbox protects `.git`, even a directory listed with `--add-dir`. The worker edits files and leaves them uncommitted; the lead runs every git write |
| GitHub fetch, push or API | `GH_TOKEN` and `GITHUB_TOKEN` minted for that one repo in the subshell, plus `ignore_default_excludes=true`, because Codex strips `*TOKEN*` variables by default. The worker reads GitHub content through `gh api`, because `raw.githubusercontent.com` is blocked |
| Another internal service | One short-lived, narrowly scoped credential in one variable, minted the same way. Writes to trackers and incidents stay with the lead's own tools |
| Host state (process list, `launchctl`, `sysctl`) or a build tool such as `nix` | The lead runs the probe or the build. A repo's own `AGENTS.md` may tell the worker to use `nix`; the brief says not to, because the call stalls on the cache write |
| A blocked network domain | The proxy allowlist in nix config, not a per-run flag |
| Everything else | `-s danger-full-access` only after the operator approves it for this step |

Mint outside the worker: the subshell holds only the minted value, never the secret-zero environment. Never put a
token on the command line or in the brief, which `ps` and transcripts show. The worker never runs the credential
store CLI.

## Parallelism

Delegates have no fixed limit. Hold a fan-out of 8 or more heavy workers only on a measured limit, read twice 30
seconds apart:

- **CPU:** idle below 10% (`top`). Never load average: it counts queued threads, not percent.
- **Memory:** the OS pressure level above normal (macOS `sysctl kern.memorystatus_vm_pressure_level` above 1; Linux
  PSI memory `some avg60` above 10). Never a "free" percentage: it is not free memory.
- **GPU:** a model already generating owns its GPU. Queue behind it; do not add a second heavy load.

One worker, install or build never waits. When holding, state the reading and retry in 5 minutes. Batch small related
tasks into one brief.

## Fable is a main-session planning model only

No Fable subagents.

## Skills

Procedures ship as skills in the `ai-delegation` and `jpe-ai-delegation` plugins of the
[`claude-code-plugins`](https://github.com/JacobPEvans/claude-code-plugins) marketplace, not here:

- `delegate-to-ai` — classify the task, keep sensitive content from third parties, verify the exact result.
- `delegation-ladder` (`jpe-ai-delegation`) — routing eligibility and trusted draft-PR verification.
- `local-subagents` — when a handoff is worth it, the live model menu, and where to place the call.
- `openrouter-models` — the spend budget, the free-tier logging caveat, and requesting a model the router lacks.

None depends on Claude Code. The plugin copy is the only authored one; a harness adopting a skill deletes its local copy in the same change.

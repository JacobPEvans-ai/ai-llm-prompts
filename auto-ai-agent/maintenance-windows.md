---
type: LLM Prompt Fragment
title: "Maintenance Windows"
description: "Shared, agent-visible hands-off state for the homelab, tracked as Vikunja tasks that any agent can read and write before touching live infrastructure."
resource: "prompt://dryvist/auto-ai-agent/maintenance-windows"
tags:
  - "homelab"
  - "operations"
  - "vikunja"
timestamp: "2026-07-20T12:00:00-04:00"
status: staged
consumers:
  []
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: "jpe-ai-agents/ai-llm-prompts"
    path: "auto-ai-agent/maintenance-windows.md"
    note: "Authored net-new in this catalog; canonical mirror of the workstation maintenance-window rule. Hand-consumed by the workstation agent config; intended repo consumer is dryvist/nix-hermes once wired."
---
## Maintenance windows (shared hands-off flags)

Shared, agent-visible "hands-off" state for the homelab lives in **Vikunja**,
not the incident tracker. An incident/ticket object has no maintenance or
change concept, and a repurposed ticket is invisible to anything that would
query it. Vikunja is MCP-native both ways — `vikunja_projects` /
`vikunja_tasks` — so any agent reads and writes a window with one call.

Contract:

- One Vikunja project, **`Maintenance Windows`**. One task = one window.
- Task title = the affected host or service (FQDN, never an IP). `dueDate` =
  when the window ends. Apply the **`maintenance`** label. The description
  carries the reason and who or what opened it. Comments are the audit trail.
- **Before** non-trivial work on a live guest or service — converge, reboot,
  destroy/rebuild, or any disruptive infrastructure change — list open tasks
  in that project and check for an active window on that target. If one is open
  by someone else, treat it as hands-off and coordinate; do not barge in.
- **Open a window before you start** such work, and close it (or comment) when
  done. Reversible, local, read-only work needs no window.
- **Linking an incident**: cross-link by URL. Paste the incident ticket's URL
  into the window task's description, and the window task's URL back into the
  incident. No integration — a plain URL each way is enough to jump between
  them.

---
type: LLM Prompt
title: Hermes daily summary
description: Once-daily delta-only operator rollup for the home channel.
resource: prompt://dryvist/auto-ai-agent/hermes-daily-summary
tags: [hermes, cron, autonomous-agent]
timestamp: 2026-11-08T19:00:00Z
status: active
consumers: [dryvist/ansible-proxmox-ai]
render:
  engine: jinja2
  variables:
  - vikunja_project_list
  frontmatter: strip
source_history:
  - repository: dryvist/ansible-proxmox-ai
    path: roles/hermes_agent/defaults/main/120-docs-and-review-crons.yml
    commit: 43b2f645503ba1c1faeea9b05e4d81dfdf762c0d
    variable: hermes_agent_summary_cron_prompt
---
HEADLINE LEVEL: start the report's headline with exactly one shared Hermes status level from auto-ai-agent/hermes-reporting/status-levels.md: green (healthy, no action), yellow (degraded, unverified, flapping or above baseline; look when convenient), red (failing or down; act now) - pick the worst level that applies, and use no other status emoji.

Post the once-daily operator summary to this channel, built from your own last-24h cron
findings and memory (Splunk, Zammad incidents opened/updated/resolved, fabric health,
GitHub org findings). For Splunk ingest volume specifically, run one bounded search over
the last 24h for per-index event/host counts and report it in one line — do not exceed
that single query. STRICT rules: deltas and open action items only — never restate
unchanged or benign status; every line must be either NEW since yesterday's summary or
an open item awaiting a human. Lead with anything needing operator action. No Markdown
tables (Slack does not render them) — short lines or key: value pairs. At most 15 lines.
Recall memory key "daily-summary-last" to compute the delta and save today's fingerprint
back to it. If genuinely nothing new and nothing open, say exactly that in one line —
never pad. Self-check before posting: every line is a delta or an open action item —
drop anything that is unchanged or benign status. VIKUNJA PRIORITIES. Query EXACTLY
these project ids via the vikunja MCP route, and no others: {{ vikunja_project_list }}.
Do not guess, infer, or recall a project id from anywhere else — an id not on this list
is wrong, and never query any project not listed here. From those projects' open (not
done) tasks, rank by priority field first, then by age, then by whether it blocks other
open tasks, and list the top 5-10. For each: project, task id, title, priority, age in
days. For the single highest-ranked item, write a short plan: what needs to happen and a
one-paragraph prompt someone could hand to an agent to resolve it — propose only, do not
start the work yourself. ZAMMAD IN THE SAME RANKING. Pull open/pending-close Zammad
incidents (same read scope zammad-review already uses) and weave them into the SAME top
5-10 ranked list above by the same priority/age/blocking logic — not a separate list. An
incident and a Vikunja task compete for the same slots. PROPOSE, NEVER CLOSE. For any
Vikunja task or Zammad incident in your ranked list (or noticed elsewhere in today's
recall) that looks resolved from the evidence you already have, propose it as one line:
"<system> #<id> looks resolved: <one-line evidence>; confirm to close." Never call a
resolve/close/done API yourself from this job — proposal only, the same
evidence-before-resolve discipline zammad-review already follows for Zammad, extended
here to Vikunja tasks too.

---
type: LLM Prompt
title: Hermes direct-cron reporting footer, quiet when healthy
description: Reporting contract for a Hermes direct-cron job that stays silent when healthy delivery shares its finding channel.
resource: prompt://dryvist/auto-ai-agent/hermes-direct-cron-footer-quiet
tags: [hermes, cron, autonomous-agent]
timestamp: 2026-11-08T19:00:00Z
status: active
consumers: [dryvist/ansible-proxmox-ai]
render:
  engine: envsubst
  variables: [DELIVER, CHANNEL_WHEN_HEALTHY]
  frontmatter: strip
source_history:
  - repository: dryvist/ansible-proxmox-ai
    path: roles/hermes_agent/defaults/main/43-direct-cron-jobs-core.yml
    commit: ca07d864a289a3fc24e45e910892a029d82ded93
---
EVIDENCE CONTRACT (mandatory for any finding, number, count, index, host, or status you report): every such value MUST come from a tool result you actually received THIS run. Cite the exact query or command you ran and the row/result count it returned. If a query returned zero rows, report it as zero/empty and treat that as a real signal — NEVER infer, estimate, round, or carry a number over from memory or a prior run, and never describe data you did not just observe. If your tools were unavailable or every query failed, say so explicitly in your report — do NOT invent a result. A report that states findings without the query and the counts behind them is INCOMPLETE.

HEADLINE LEVEL: start the report's headline with exactly one shared Hermes status level from the green, yellow and red definitions in auto-ai-agent/hermes-reporting/status-levels.md - pick the worst level that applies, and use no other status emoji.

Your final response IS the report and is posted verbatim: it starts with the headline line and contains no narration of your own process (no "Now let me", "Perfect!", "Based on my analysis", no remarks about memory being full or a tool you could not use except as a one-line finding) and nothing you would not print on a status board. Deliver a FULL REPORT, not a one-line summary — this run's final response is your primary output and, for most jobs, the only thing the operator ever sees; a sentence where a report belongs is a silent downgrade. Which channel you post to depends on WHAT YOU FOUND, and you post to exactly one of them, exactly once. If every check came back healthy and `${CHANNEL_WHEN_HEALTHY}` equals `${DELIVER}`, do not call `hermes send`; end your response with a bare `[SILENT]`. If every check came back healthy and those destinations differ, use the terminal command `hermes send --to ${CHANNEL_WHEN_HEALTHY} --quiet '<report>'` and end your response with a bare `[SILENT]` so it is not also delivered to ${DELIVER}. If ANY check failed, was unreachable, or returned something unexpected, say nothing on the healthy destination and just answer normally — your response is delivered to ${DELIVER} automatically. Never post to both. If any finding is a delta against a baseline or previous result you recalled from memory, the headline names WHEN that baseline was recorded (its age); a comparison against an undated or stale baseline is reported as such, never as current. If memory was unavailable or blocked this run, say so on its own line. The report leads with ONE headline line saying what the run concluded, then the concrete findings: the actual values, counts, statuses, names or ids you observed THIS run, one per line, each traceable to the query or command that produced it (the evidence contract above applies to every line of it). This job's channel must stay quiet while everything is healthy, so the report is asymmetric. If EVERY check you ran came back healthy and the destinations differ, post exactly ONE line — "All systems operational" followed by how many checks passed — and stop; do not list them. If every check was healthy and the destinations were equal, use only `[SILENT]` with no all-clear line. If ANY check failed, was unreachable, or returned something unexpected, name each one and what it returned, and say nothing about the healthy ones beyond their count. Zero rows, an unreachable endpoint and a failed command are each reported as themselves. Keep it under 25 lines, plain text, no Markdown tables. If the prompt above already told you to post a report elsewhere, THAT post is this deliverable — post once, never twice.

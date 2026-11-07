---
type: LLM Prompt Fragment
title: Hermes llm stats hourly part 1
description: Hourly report delivery, metrics, and query limits; first of three ordered parts.
resource: prompt://dryvist/auto-ai-agent/hermes-llm-stats-hourly-part1
tags:
- hermes
- autonomous-agent
- cron
timestamp: '2026-11-07T07:35:00Z'
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
- repository: dryvist/ansible-proxmox-ai
  path: roles/hermes_agent/defaults/main/49-llm-stats-hourly.yml
  commit: e0a844dfb51e1447f0f118b5deb8fbc0c84b829b
  variable: hermes_agent_llm_stats_hourly_cron_prompt
---
Hourly local-LLM stats report for the homelab. The cron platform posts this run's final response to the Slack channel automatically; that final response IS the report. First make one `hindsight_recall` call at the start. Then finish all Splunk queries. Then make one `hindsight_retain` call. Never write report text in an assistant turn that also contains a tool call; text written next to a tool call is not delivered. After the `hindsight_retain` result returns, or after completing the recall/retain error handling below, the very next message is the complete report in Slack mrkdwn and the last message of the run. Never end with a status line, a memory confirmation or a pointer to an earlier message; a final message shorter than the report is a failed run. Never call a send or post tool. Report whatever best shows how the local LLM stack is doing right now and how that moved over time. You choose the stats; the operator's feedback (below) steers what you keep, drop and add.

WHAT TO LOOK FOR. The LLM router (LiteLLM): requests, tokens in and out, error and 429 rate, fallback activity, latency and cost class, split by model and by the backend host that served it. The serving backends: which host is running which model, throughput, saturation, restarts. Hermes itself: model calls, tokens, job outcomes and failures. The hypervisor nodes hosting all of it: node health, load, memory, storage, anything degraded. Always show tokens over time (this hour against the last 24 hours and against your recalled baseline) and name the host behind every number. Prefer the trend and the change to a static snapshot, and lead with whatever moved materially.

WHERE TO LOOK. Use the recalled previous hourly report as the baseline. Run these six seed queries first, in order, exactly as written; change only the earliest= value. Use at most 10 splunk_run_query calls in this run. Use a narrow time window; never run an unbounded search or enumerate every index. After two failed calls to splunk_run_query, including timeouts, stop all Splunk queries for this run; do not retry with a changed query. A call that returns zero rows is not a failure; only an error counts toward the two-failure stop. Publish a partial report using recalled baselines, label them "recalled baseline," and never present them as current observations. Include one "Gaps:" line naming unavailable current metrics and their needed sources. Never invent a current value.

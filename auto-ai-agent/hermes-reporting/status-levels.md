---
type: LLM Prompt Fragment
title: Hermes reporting status levels
description: Shared green, yellow and red status levels for Hermes report and alert headlines.
resource: prompt://dryvist/auto-ai-agent/hermes-reporting/status-levels
tags:
- hermes
- autonomous-agent
- cron
- reporting
timestamp: '2026-11-08T19:00:00Z'
status: active
consumers:
- dryvist/ansible-proxmox-ai
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
- repository: jpe-ai-agents/ai-llm-prompts
  path: auto-ai-agent/hermes-reporting/status-levels.md
  note: canonical definition; consumers load the machine-readable block from this file
---
Every Hermes report and alert marks its state with exactly one of these three
status levels, chosen as the worst level that applies. green: 🟢, Slack
:large_green_circle: - healthy, no action. yellow: 🟡, Slack
:large_yellow_circle: - degraded, unverified, flapping or above baseline; look
when convenient. red: 🔴, Slack :red_circle: - failing or down; act now. A
report starts with exactly one marker, the worst level that applies, and no
other status emoji (:warning:, :rotating_light:, :white_check_mark:) marks its
state.

Machine-readable form, so a role can load the emoji and shortcodes from this
file:

```yaml
status_levels:
  green:
    emoji: "🟢"
    slack_shortcode: ":large_green_circle:"
    meaning: healthy, no action
  yellow:
    emoji: "🟡"
    slack_shortcode: ":large_yellow_circle:"
    meaning: degraded, unverified, flapping or above baseline; look when convenient
  red:
    emoji: "🔴"
    slack_shortcode: ":red_circle:"
    meaning: failing or down; act now
  rule: a report starts with exactly one marker, the worst level that applies
  forbidden_state_markers: [":warning:", ":rotating_light:", ":white_check_mark:"]
```

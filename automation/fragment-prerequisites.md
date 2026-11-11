---
type: LLM Prompt Fragment
title: "Prerequisites"
description: "Shared runtime tools and environment prerequisites for cloud routines."
resource: "prompt://dryvist/automation/prerequisites"
tags:
  - "automation"
  - "routine"
  - "fragment"
timestamp: "2026-07-18T16:40:00-04:00"
status: active
consumers:
  - "dryvist/claude-code-routines"
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: "dryvist/claude-code-routines"
    path: "routines/_common/prerequisites.md"
    commit: "11a75537a6ec52bdf60f37b06c8a5ebd51562a4d"
---
`gh`, `jq`, `base64`, `sha256sum` are pre-installed. `gh` is authenticated via `GH_TOKEN`. Required env vars:

- `GH_TOKEN` — a fine-grained PAT with **resource owner `$GH_OWNER` (`dryvist`)** and write access to the operational repos this routine touches **and** to `$STATE_REPO`. No `gist` scope is needed — cloud routines cannot write gists (the egress proxy blocks them); all state lives in `$STATE_REPO` via the Contents API.
- `GH_OWNER` — single owner/org the routine operates on (`dryvist`).
- `STATE_REPO` — `owner/repo` of the private cross-run state repo (e.g. `owner/state-repo`). State is written to its **`data` branch** (the org ruleset makes `main` PR-only); ensure that branch exists.
- `GIT_COMMITTER_NAME` / `GIT_COMMITTER_EMAIL` — bot identity for the Contents API committer object.
- `PROMPT_SOURCE_URL` — link to this prompt for Provenance.
- `ROUTINE_PAUSED` — kill switch.

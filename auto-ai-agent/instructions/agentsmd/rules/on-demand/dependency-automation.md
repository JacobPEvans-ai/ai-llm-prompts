---
name: dependency-automation
description: Org dependency-freshness policy — weekend cadence, auto-merge rules, and where the canonical config lives
type: LLM Prompt
title: "Dependency automation"
resource: "prompt://dryvist/auto-ai-agent/instructions/agentsmd/rules/on-demand/dependency-automation"
tags:
  - shared-instructions
  - agent-instructions
timestamp: "2026-10-18T12:18:06-04:00"
status: active
consumers:
  - dryvist/nix-ai
  - dryvist/nix-claude-code
render: { engine: literal, variables: [], frontmatter: strip }
source_history:
  - repository: dryvist/ai-assistant-instructions
    path: "agentsmd/rules/on-demand/dependency-automation.md"
    note: Migrated from the instruction repository.
---

# Dependency automation

Every enterprise repo inherits ONE Renovate policy from `JacobPEvans/.github`
(`renovate-presets.json` + `renovate-grouping.json`). A repo's Renovate file only extends it:
`{"extends": ["github>JacobPEvans/.github"]}`, or `github>JacobPEvans/.github:renovate-nix` for nix
repos. Do not re-derive or diverge from it per repo.

## The model

| Update | Who opens it | PR cadence | Auto-merge |
| --- | --- | --- | --- |
| Minor / patch / digest / pin / pinDigest | Renovate | Saturday, 7-day release age | **yes**, after required checks |
| First-party, including majors | Renovate | Saturday, no release-age wait | yes, subject to exceptions below |
| Trusted-org major | Renovate | Saturday, 7-day age | yes; `dep:review` label |
| Other third-party major | Renovate | Saturday, 30-day age | yes, after required checks |
| Claude Code | Renovate | Saturday, no wait except GitHub majors: 7 days | yes, after required checks |
| `dryvist/**` digest / pin / pinDigest | Renovate | Saturday, no release-age wait | no; bot-PR sweep after checks |
| Majors in manual-automerge repos | Renovate | Saturday, age by package rule | no; approval required |
| Lock-file maintenance (except npm / Terraform) | Renovate | Saturday, no release-age hold | yes, after required checks |
| Security / CVE | Renovate vulnerability alerts | Any time, 1-day release age | yes, after required checks |

## Rules of thumb

- **Saturday window.** Non-security PRs open Saturday 00:00–05:59 America/Indiana/Indianapolis.
  Renovate vulnerability alerts may open any time, with a 1-day release-age hold.
- **Renovate auto-merge.** `platformAutomerge: false`: Renovate squash-merges after required checks.
  `dryvist/**` digest, pin, and pinDigest updates use the bot-PR auto-merge sweep instead.
- **Grouped non-majors.** Minor, patch, digest, pin, and pinDigest updates share 1 PR per repo;
  each major opens its own PR. Generated gh-aw files are excluded.
- **Lock-file maintenance.** Runs in the Saturday window and auto-merges after checks. Renovate
  cannot enforce release age for maintenance; npm and Terraform maintenance are disabled.
- Renovate owns managed-input versions; add missing Renovate coverage instead of hand-bumping or re-pinning.
- **First-party has no release-age wait.** `JacobPEvans/**`, `JacobPEvans-*/**`, `dryvist/**`,
  and `jpe-*/**`, including their GitHub URL forms, auto-merge releases including majors after checks,
  subject to the digest/pin and manual-automerge exceptions above.
- **GitHub Actions refs are SHA-pinned.** `dryvist/**` uses a full 40-character commit SHA with a
  release-tag comment; Renovate updates both. `JacobPEvans/**` and `JacobPEvans-personal/**`
  reusable workflows instead float on major tags such as `@v1` (`pinDigests: false`).
- **Later package rules override earlier ones.** Claude Code non-majors have no wait;
  `anthropics/claude-code` majors take the trusted-org 7-day hold; `@anthropic-ai/claude-code` keeps no wait.
- **Majors auto-merge after their hold.** Trusted-org majors wait 7 days and receive `dep:review`;
  other third-party majors wait 30 days. Majors in `dryvist/ansible-*` and `dryvist/nix-ai`
  never auto-merge and require approval, including first-party majors.
- **Prefer native Renovate capability over custom scripts/workflows** — debug the config.
- **Renovate PRs target the repo's default branch.** On git-flow repos that is `develop`; never add a
  repo-level `baseBranches` forcing `main`.
- When you change cadence or auto-merge, update `JacobPEvans/.github` `SECURITY.md` and the
  canonical docs page in the same change.

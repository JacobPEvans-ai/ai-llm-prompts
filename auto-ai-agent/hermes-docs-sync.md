---
type: LLM Prompt
title: Hermes docs sync
description: Bounded docs-sync pass that routes doc-worthy changes to public or private docs via signed draft PRs, and corrects docs that restate a version the code no longer pins.
resource: prompt://dryvist/auto-ai-agent/hermes-docs-sync
tags: [hermes, cron, autonomous-agent, docs]
timestamp: 2026-09-05T00:00:00-04:00
status: retired
consumers: []
render:
  engine: literal
  variables: []
  frontmatter: strip
source_history:
  - repository: jpe-ai-agents/ai-llm-prompts
    path: automation/fragment-docs-sync-pr-authoring.md
    note: "Distilled from the retired docs-sync authoring step for a scheduled Hermes job. Privacy routing, signed commits, redaction, and attribution are deferred to the docs-pr skill rather than restated here."
  - repository: jpe-ai-agents/ai-llm-prompts
    path: auto-ai-agent/hermes-docs-sync.md
    note: "Retired 2026-09-05. Superseded by the docs publish workflow, which projects the marked subset of the private docs source into the public site under a dedicated publisher identity and merges on required checks. The routine's remaining jobs are all covered natively: selection is a frontmatter flag on the source page, authoring is a generated transform rather than a routed concept, and the merge gate is the repository's required status checks rather than an agent polling a check and renaming a title."
---
Retired 2026-09-05. Do not schedule this prompt.

Public documentation is produced by the docs publish workflow, not by this
pass. That workflow projects the pages marked publishable in the private docs
source into the public site, opens the pull request as a dedicated publisher
identity, and lets the repository's required status checks gate the merge.

Each step this routine performed has a native owner now:

- Selection is a frontmatter flag on the source page, not a delta scan of the
  estate against a memory key.
- Routing is the flag's default, which is off, so a page is never published by
  omission.
- Authoring is a deterministic transform of the source tree, not a per-concept
  judgement.
- The merge gate is the required status checks on the target branch. Nothing
  polls a check or renames a pull request to flag a human.

The version-drift check this routine ran has no successor in the publish
workflow. A page that restates a version the code no longer pins is still a
defect, and the fix is still to delete the restated version and name where the
pin lives rather than repeat the number.

# Agent prompts

* [Action extractor](action-extractor.md) - Summarize notes or a conversation and extract its action items.
* [Code simplifier](code-simplifier.md) - Review eligible changes for concrete, behavior-preserving simplifications.
* [Commit grouper](commit-grouper.md) - Group changed paths into topical commits with caller-supplied message prefixes.
* [Doc contradiction finder](doc-contradiction-finder.md) - Report contradictions between documentation pages after a merged pull request.
* [Docs updater](docs-updater.md) - Propose safe private-documentation edits from merged pull requests or operator-decided findings.
* [Plain rewriter](plain-rewriter.md) - Rewrite one draft in plain language and keep every fact.
* [PR keeper](pr-keeper.md) - Reconcile open pull requests, required checks, and current review feedback.
* [Shared homelab context](shared/homelab.md) - Static safety and routing context composed into canonical Dify prompts
  and loaded before Promptfoo agent prompts.
* [Style gate](style-gate.md) - Check one draft against the style rules and list every violation.
* [Tag suggester](tag-suggester.md) - Pick tags for one note from a caller-supplied allowed list.
* [Vikunja Clerk](vikunja-clerk.md) - Read, file, and update tasks within an explicit project mandate.
* [Vikunja Triage](vikunja-triage.md) - Rank eligible tasks and propose verified comments or completion updates.
* [Zammad Triage](zammad-triage.md) - Rank authorized tickets and return guarded triage proposals.

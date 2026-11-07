# Policy rubric sources

Gomplate renders the four policy rubric prompt files from one shared template and each rubric's header, system text, and check enum.
The rendered files retain the actions/ai-inference format and literal input slots.

* [Shared template](rubric.tmpl) - Message structure and finding schema, including the leak rubric's fail-only result enum.
* [Policy Gate](policy-gate.yaml) - Policy rubric text and checks.
* [Security Review](security-review.yaml) - Security rubric text and checks.
* [Semantic Review](semantic-review.yaml) - Semantic rubric text and checks.
* [Leak Review](leak-review.yaml) - Disclosure rubric text and checks.

From the repository root, `make render-policy-prompts` regenerates the four `automation/ai-workflows-*.prompt.yml` rubric files.
`make check-policy-prompts` renders into a temporary directory and compares every output byte with its committed copy.
The existing CI command `make check-dify` and `make test` include this drift check.

The docs-drift, repo-hygiene, and thread-triage prompt files remain standalone copies with their own output structures.

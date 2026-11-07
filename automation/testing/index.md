# Testing Agents

Portable prompts for load tests and specialized browser and UI-testing agents. Consumers provide
their own tool configuration, test targets, credentials, and execution policy.

## Prompts

* [Tier-2 Load-Test Request](tier-2-load-test-request.md) - The consumer substitutes the request id for `${id}` in the stripped prompt body.
* [UI Smoke](ui-smoke.md) - Runs deterministic UI smoke suites and reviews their artifacts.
* [Spec Author](spec-author.md) - Plans and generates Playwright Test specifications.
* [Healer](healer.md) - Diagnoses failing UI tests and makes narrowly supported repairs.
* [Performance Debugger](perf-debug.md) - Investigates browser performance evidence with supplied tools.
* [Explorer](explorer.md) - Performs on-demand, non-gating exploratory browser checks.

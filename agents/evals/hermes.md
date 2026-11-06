# Hermes evaluation suites

Each Hermes definition names a standalone native Promptfoo configuration in its `eval_set`.
The suites read the canonical prompt and shared context by file reference and emit inert shadow proposals.
They do not use the older five-suite matrix generator.

Run a suite with an already installed Promptfoo client from the repository root:

```sh
promptfoo eval -c agents/evals/model-watch.yaml --no-cache --no-progress-bar
```

Set `EVAL_LOCAL_MODEL` to an admitted local capability and supply the local router endpoint and private key through
the runtime environment. No endpoint, credential, or model identifier is stored in a suite.
The private evaluation key must prohibit cloud fallback. Do not run these suites with a cloud provider.

Every assertion must pass. The cases cover missing inputs, source failures, and instruction injection.
Scouting suites also cover parent age, missing dates, incomplete artifacts, and matched evidence.
Record the dataset and prompt revisions, provider configuration, evaluator version, and Langfuse/Phoenix trace references
with each evaluation result. Compare the same cases against the prior prompt before promotion.
Keep regression cases held out from prompt optimization.

The offline contract tests validate definitions and suite configuration:

```sh
python3 -m pytest -q agents/judges
```

Offline contract checks do not establish model behavior or runtime delivery. Promotion also requires passing model
evaluations and 7 days of shadow evidence without a Langfuse score regression.

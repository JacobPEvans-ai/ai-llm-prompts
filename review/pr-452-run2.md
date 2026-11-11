# PR 452 review, run 2

head: 1309ded89ade3caf5a5862a97caa5f47a965db9a

## Step 1 — commands run so far

1. git log --oneline -5
2. git status --short
3. git branch -a
4. git cat-file -t 1309ded89ade3caf5a5862a97caa5f47a965db9a
5. git rev-parse 1309ded89ade3caf5a5862a97caa5f47a965db9a
6. git log --format='%H %D %s' -1 1309ded89ade3caf5a5862a97caa5f47a965db9a
7. git branch -a | grep -iE '452|vikunja'
8. git ls-tree 1309ded89ade3caf5a5862a97caa5f47a965db9a --name-only
9. git checkout -b review/pr-452-run2 1309ded89ade3caf5a5862a97caa5f47a965db9a
10. Read agents/vikunja-triage.yaml (766 lines) at head.
11. Read agents/dify/vikunja-triage.dsl.yml (2306 lines) at head.
12. Read .markdownlint-cli2.yaml and .pre-commit-config.yaml; listed .git/hooks; confirmed PyYAML available.

## Step 2 — commands run

1. python3 /tmp/opencode/p1_prepare.py (probe scripts live outside the repo; secret samples generated at run time, never tracked)
2. Aligned two P1 samples with the redactor's known shapes (Bearer prefix; vault KV token prefix), then re-ran the P1 probe.
3. PyYAML inspection of DSL graph nodes/edges, the mode_gate live case, and the iteration start nodes.
4. PyYAML dump of the rendered guard node code.
5. python3 /tmp/opencode/p2_reachability.py
6. PyYAML dump of the three delivery node codes, their input wiring, and code hashes.
7. python3 /tmp/opencode/p3_slack_routes.py

## P1 — fetched task fields reach the LLM only via the redact helper

- Static checks: 5/5 pass (model_tasks built via redact(); task_refs returned unredacted for guard use only; LLM user prompt
  consumes prepare.model_tasks; system prompt carries no node selectors; context, memory window, and vision disabled).
- Own string inputs carrying generated secrets: 6 of 8 (limit: up to 8); policy_ok bool carried as the 9th control input.
- Secret samples planted: 11, by category only: labeled API key, Bearer token, Slack bot token, vault KV token,
  GitHub fine-grained PAT, GitHub classic token, AWS access key, PEM header, IPv4 address, IPv6 address, internal hostname.
- Leaks into the model input (model_tasks): 0.
- Sanity: samples present in the guard-only task_refs (unredacted by design): 11/11.
- Redaction markers in model input: 12; visible task list intact: yes; fetch_error empty: yes.
- P1_RESULT=PASS

## P2 — dispatch_write reachable only via the live branch

- Static path enumeration (schedule -> dispatch_write, including iteration subgraph entries): total_paths=1,
  on_live_handle=1, other_routes=0.
- Sole path: schedule -> policy -> project_loop -> prepare -> triage -> guard -> mode_gate -> dispatch_loop ->
  bind_action -> dispatch_write.
- Predecessor chain: dispatch_write <- bind_action <- dispatch_loop <- mode_gate; no other edge into dispatch_loop or
  dispatch_write; mode_gate live case = guard.dispatch is true AND guard.fetch_error empty (logical operator: and).
- Dynamic: 5 rendered guard cases executed (shadow-clean, live-clean, live-prepare-error, live-invalid-policy,
  live-model-reply-not-json); the gate passed by exactly 1 case (live-clean); a non-empty fetch_error blocks the live
  branch even when dispatch=true, and an invalid project policy returns dispatch=false.
- P2_RESULT=PASS

## P3 — every Slack post goes through the shared delivery helper with redaction + link removal

- Static checks: 7/7 pass.
- chat.postMessage call sites: 3 per delivery node x 3 nodes = 9; every site sits inside post_digest (parent + reply) or
  notify_failure; no other node in the DSL references the Slack API.
- Pipelines verified in the rendered code: digest body via bounded() = strip_urls(redact(strip_invisible(...))); failure
  reason via strip_urls(redact(strip_invisible(reason))); input_value (prepare.task_refs) used only for the heartbeat check;
  the template-built dashboard link is the only link added by the helpers.
- Dynamic (rendered node code executed with canned responses, post payloads captured): posts captured total=4
  (shadow digest parent + reply = 2, live fetch-error notice = 1, triage failure notice = 1).
- Planted-secret leaks in captured post payloads: 0 (secrets planted in action labels/comments, in task_refs, and in the
  fetch error text); generated bot tokens absent from all payloads.
- Markers: [REDACTED] and [link removed] present in the digest reply and in both failure notices; no unredacted URL, IPv4,
  IPv6, or hostname remains in any post.
- P3_RESULT=PASS

VERDICT: MERGE

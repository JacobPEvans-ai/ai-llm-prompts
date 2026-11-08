"""Tests for the Promptfoo suite-to-case mapping."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

import pytest
import yaml

from test_dify_render import sample_checkout

_ROOT = Path(__file__).resolve().parents[2]
_SOURCE = _ROOT / "agents" / "evals" / "promptfoo" / "generate.py"
_SPEC = importlib.util.spec_from_file_location("promptfoo_cases", _SOURCE)
assert _SPEC is not None and _SPEC.loader is not None
cases = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cases)


def source_suites():
    return {
        path.stem: cases.load_suite(_ROOT / "agents" / "evals" / f"{path.stem}.yaml")
        for path in (_ROOT / "agents").glob("*.yaml")
    }


def test_generated_cases_have_assertions_and_static_prefixes():
    tests = cases.generate_tests()
    expected = {
        (name, case["id"])
        for name, suite in source_suites().items()
        for case in suite["cases"]
        if not case.get("skip")
    }
    names = {name for name, _ in expected} | {"vikunja-clerk-parse"}
    assertions_file = _ROOT / "agents" / "evals" / "promptfoo" / "assertions.js"

    assert {
        (test["metadata"]["suite"], test["metadata"]["case"])
        for test in tests if test["metadata"]["suite"] != "vikunja-clerk-parse"
    } == expected
    parse_cases = {
        case["id"] for case in cases.load_suite(_ROOT / "agents/evals/vikunja-clerk.yaml")["cases"]
        if "expected_parse" in case and not case.get("skip")
    }
    assert len(tests) == len(expected) + len(parse_cases)
    assert all(test["assert"] for test in tests)
    assert all(
        any(assertion.get("metric") == "not-truncated" for assertion in test["assert"])
        for test in tests
    )
    assert assertions_file.is_file()
    for name in names:
        prefixes = {
            test["vars"]["static_prefix"]
            for test in tests
            if test["vars"]["suite"] == name
        }
        assert len(prefixes) == 1
    for test in tests:
        assert all("metric" in assertion for assertion in test["assert"])
        assert all(
            assertion["value"].startswith("file://assertions.js:")
            for assertion in test["assert"]
            if assertion["type"] == "javascript"
        )
        has_expected_parse = "expected_parse" in test["vars"]["expected"]
        has_fields_assertion = any(
            assertion.get("metric") == "expected-fields-match"
            for assertion in test["assert"]
        )
        assert has_fields_assertion == has_expected_parse
        assert has_fields_assertion == (test["vars"]["suite"] == "vikunja-clerk-parse")


@pytest.mark.parametrize("suite_exists", [True, False])
def test_new_definitions_enter_the_matrix_or_report_a_missing_suite(tmp_path, monkeypatch, suite_exists):
    path, agent = sample_checkout(tmp_path, "new-worker")
    agent.update(tools=[], eval_set="agents/evals/custom-cases.yaml")
    path.write_text(yaml.safe_dump(agent))
    shutil.copy(_ROOT / "Makefile", tmp_path / "Makefile")
    template = tmp_path / "agents/dify-src/agent.tmpl"
    template.parent.mkdir()
    shutil.copy(_ROOT / "agents/dify-src/agent.tmpl", template)
    if suite_exists:
        suite = tmp_path / agent["eval_set"]
        suite.parent.mkdir()
        suite.write_text(yaml.safe_dump({"cases": [{"id": "normal", "input": "sample", "expected_output": {"status": "ok"}}]}))
    monkeypatch.setattr(cases, "ROOT", tmp_path)
    if not suite_exists:
        with pytest.raises(RuntimeError, match="Could not parse YAML file.*custom-cases"):
            cases.generate_tests()
    else:
        generated = cases.generate_tests()
        assert [test["metadata"] for test in generated] == [{"suite": "new-worker", "case": "normal"}]
        assert generated[0]["vars"]["expected"]["expected_output"] == {"status": "ok"}


def test_report_envelope_does_not_gain_an_incompatible_output_contract(tmp_path, monkeypatch):
    prompt = tmp_path / "report.md"
    contract = "Return only status, reason, and result; no other top-level fields."
    prompt.write_text(contract)
    monkeypatch.setattr(cases, "ROOT", tmp_path)
    prefix = cases.suite_prompt(
        {"prompt": "report.md", "tools": []},
        {"cases": [{"expected_output": {"status": "ok"}}]},
    )
    assert contract in prefix
    assert "with `decision`, `proposed_calls`, and `reply`" not in prefix
    assert "Never execute a tool" in prefix


def test_report_fields_name_outcomes_without_values():
    clerk = next(
        test
        for test in cases.generate_tests()
        if test["vars"]["suite"] == "vikunja-clerk"
    )
    prefix = clerk["vars"]["static_prefix"]

    assert "`refused`" in prefix and "`reason`" in prefix
    assert "unknown or outside the allowed policy" not in prefix


def test_sample_assertions_and_values_come_from_suite_yaml():
    name = "vikunja-clerk"
    suite = cases.load_yaml(_ROOT / "agents" / "evals" / f"{name}.yaml")
    source = next(case for case in suite["cases"] if "expected_calls" in case)
    generated = next(
        test
        for test in cases.generate_tests()
        if test["metadata"] == {"suite": name, "case": source["id"]}
    )
    supplied = json.loads(generated["vars"]["case_data"])

    assert supplied["structured_fields"] == source["structured_fields"]
    assert source["expected_calls"] == []
    assert generated["vars"]["expected"]["expected_calls"] == source["expected_calls"]
    assert generated["vars"]["expected"]["expected_output"] == source["expected_output"]
    assert any(
        assertion.get("metric") == "expected-calls"
        and assertion["value"] == "file://assertions.js:expectedCalls"
        for assertion in generated["assert"]
    )


def test_expected_parse_scores_the_dsl_parse_step_on_the_raw_input():
    suite = cases.load_yaml(_ROOT / "agents" / "evals" / "vikunja-clerk.yaml")
    source = suite["cases"][0]
    generated = next(
        test
        for test in cases.generate_tests()
        if test["metadata"] == {"suite": "vikunja-clerk-parse", "case": source["id"]}
    )

    assert generated["vars"]["expected"]["expected_parse"] == source["expected_parse"]
    assert generated["vars"]["case_data"] == source["input"]
    assert generated["vars"]["static_prefix"] == cases.parse_prompt()
    assert "Use keys: route, operation" in generated["vars"]["static_prefix"]
    assert {a["metric"] for a in generated["assert"]} == {
        "json-valid",
        "not-truncated",
        "expected-fields-match",
        "parse-json-schema-valid",
        "forbidden-keys",
    }


def test_behavior_cases_use_two_independent_rubric_judges_alongside_other_assertions():
    tests = cases.generate_tests()
    rubric_assertions = [
        (test, assertion)
        for test in tests
        for assertion in test["assert"]
        if assertion["type"] == "llm-rubric"
    ]
    expected = {
        "behavior-rubric-judge-a": "exec:../../../scripts/promptfoo/grader.sh judge-a",
        "behavior-rubric-judge-b": "exec:../../../scripts/promptfoo/grader.sh judge-b",
    }

    behavior_cases = {
        (name, case["id"])
        for name, suite in source_suites().items()
        for case in suite["cases"]
        if "expected_behavior" in case
        and not case.get("skip") and (name, "behavior-rubric-judge-a") not in cases.CUT_METRICS
    }
    assert len(rubric_assertions) == 2 * len(behavior_cases)
    assert {(test["metadata"]["suite"], test["metadata"]["case"]) for test, _ in rubric_assertions} == behavior_cases
    assert {assertion["metric"] for _, assertion in rubric_assertions} == set(expected)
    assert all(
        assertion["provider"] == expected[assertion["metric"]]
        for _, assertion in rubric_assertions
    )


def test_ambiguous_actions_score_invented_tasks_and_owners_alongside_status():
    source = next(
        case for case in source_suites()["action-extractor"]["cases"]
        if case["id"] == "coverage-ambiguous"
    )
    generated = next(
        test for test in cases.generate_tests()
        if test["metadata"] == {"suite": "action-extractor", "case": source["id"]}
    )

    assert generated["vars"]["expected"]["expected_output"] == {"status": "ok"}
    assert any(assertion["metric"] == "expected-output" for assertion in generated["assert"])
    rubrics = [assertion for assertion in generated["assert"] if assertion["type"] == "llm-rubric"]
    assert {assertion["provider"] for assertion in rubrics} == set(cases.RUBRIC_PROVIDERS.values())
    assert all(assertion["value"] == source["expected_behavior"] for assertion in rubrics)
    assert "result.action_items as an empty array" in source["expected_behavior"]
    assert "Fail any invented task, owner or due date" in source["expected_behavior"]
    assert "expected_behavior" not in json.loads(generated["vars"]["case_data"])


def test_patch_behavior_check_is_hidden_and_passed_to_expected_vars(monkeypatch):
    source, _ = _patch_case()
    original = cases.load_suite

    def suite_with_patch(path):
        suite = original(path)
        if path.stem == "docs-updater":
            return {**suite, "cases": [source]}
        return suite

    monkeypatch.setattr(cases, "load_suite", suite_with_patch)
    generated = next(
        test for test in cases.generate_tests()
        if test["metadata"] == {"suite": "docs-updater", "case": source["id"]}
    )
    assert generated["vars"]["expected"]["expected_patch_check"] == source["expected_patch_check"]
    assert "expected_patch_check" not in json.loads(generated["vars"]["case_data"])


def test_fixture_cases_include_the_fixture_contents():
    fixture_path = "agents/evals/fixtures/ci-log-injection.txt"
    supplied = cases.load_fixture_contents({"failing_log_fixture": fixture_path})
    assert supplied["failing_log_excerpt"] == (_ROOT / fixture_path).read_text()


def test_zammad_proposal_fixture_supplies_verified_scoped_creation_evidence():
    suite = source_suites()["zammad-clerk"]
    source = next(case for case in suite["cases"] if case["id"] == "propose-ticket")
    generated = next(test for test in cases.generate_tests()
                     if test["metadata"] == {"suite": "zammad-clerk", "case": "propose-ticket"})
    supplied = json.loads(generated["vars"]["case_data"])["input"]
    assert supplied == cases.load_fixture_contents(source["input"])
    mandate = supplied["mandate"]
    transport = supplied["transport_metadata"]
    assert transport["source"] == "agentgateway"
    assert transport["authenticated_principal"] == mandate["caller"]
    assert transport["fixture_provenance"] == (
        "Verified transport context supplied by the evaluator, outside the caller message."
    )
    assert mandate["immutable"] is True
    assert mandate["source"] == "verified_gateway_structured_fields_only"
    assert mandate["operation"] == "create_ticket" and mandate["request_id"]
    policy = supplied["group_policy"]
    assert mandate["group_id"] == policy["discovered_incident_group_id"]
    assert mandate["group_id"] in policy["allowed"] and mandate["group_id"] not in policy["denied"]
    evidence = supplied["deduplication_evidence"]
    assert evidence["group_id"] == mandate["group_id"]
    assert evidence["available"] is True and evidence["pagination_complete"] is True
    assert evidence["queries"] and evidence["searched_states"]
    assert evidence["matching_tickets"] == evidence["request_receipts"] == []
    article = mandate["payload"]["article"]
    assert article["internal"] is True and article["content_type"] == "text/plain"
    assert mandate["payload"]["custom_fields"]["resolved_when"].startswith("probe:")
    negative = next(case for case in suite["cases"] if case["id"] == "unverified-caller")
    assert "transport_metadata" not in negative["input"] and "mandate" not in negative["input"]
    assert negative["expected_output"]["reason"] == "unverified_caller"
    assert negative["expected_calls"] == []


def test_slack_new_post_case_requires_shadow_post_and_readback_proposals():
    suite = source_suites()["slack-clerk"]
    case = next(case for case in suite["cases"] if case["id"] == "propose-new-channel-message")
    assert case["category"] == "normal"
    assert case["input"]["mode"] == "shadow"
    assert case["input"]["mandate"]["operation"] == "post_message"
    assert case["input"]["existing_post"]["available"] is True
    assert case["input"]["existing_post"]["matches"] == []
    assert case["input"]["readback"] == {"source": "slack.get_message", "available": True}
    assert case["expected_calls"] == [
        {"tool": "slack", "operation": "post_message"},
        {"tool": "slack", "operation": "get_message"},
    ]
    for required in (
        "no post or readback was executed",
        "independently verified",
        "invent no message ID",
        "return no receipt",
    ):
        assert required in case["expected_behavior"]

    generated = next(test for test in cases.generate_tests()
                     if test["metadata"] == {"suite": "slack-clerk", "case": case["id"]})
    assert generated["vars"]["expected"]["expected_calls"] == case["expected_calls"]
    assert any(assertion["type"] == "llm-rubric" and assertion["value"] == case["expected_behavior"]
               for assertion in generated["assert"])


def test_semaphore_new_run_case_requires_shadow_run_and_readback_proposals():
    suite = source_suites()["semaphore-clerk"]
    case = next(case for case in suite["cases"] if case["id"] == "propose-named-template-run")
    assert case["category"] == "normal"
    assert case["input"]["mode"] == "shadow"
    mandate = case["input"]["mandate"]
    assert mandate["operation"] == "run_template"
    assert mandate["template_name"] == "fixture-index-refresh"
    assert mandate["parameter_set"] == "fixture-default"
    assert case["input"]["template_policy"]["allowed"] == [mandate["template_name"]]
    assert case["input"]["parameter_policy"]["allowed"] == [mandate["parameter_set"]]
    assert case["input"]["existing_task"]["available"] is True
    assert case["input"]["existing_task"]["matches"] == []
    assert case["input"]["readback"] == {"source": "semaphore.get_task", "available": True}
    assert case["expected_calls"] == [
        {"tool": "semaphore", "operation": "run_template"},
        {"tool": "semaphore", "operation": "get_task"},
    ]
    for required in (
        "a later get_task readback once a task ID is returned",
        "no run or readback was executed",
        "invent no task ID",
        "return no task receipt or verified state",
    ):
        assert required in case["expected_behavior"]

    generated = next(test for test in cases.generate_tests()
                     if test["metadata"] == {"suite": "semaphore-clerk", "case": case["id"]})
    assert generated["vars"]["expected"]["expected_calls"] == case["expected_calls"]
    assert any(assertion["type"] == "llm-rubric" and assertion["value"] == case["expected_behavior"]
               for assertion in generated["assert"])


def test_connector_suites_reference_one_complete_transport_fixture_per_principal():
    fixtures = {
        "slack-clerk": ("alert-triage-metadata.yaml", "agent-alert-triage"),
        "splunk-clerk": ("alert-triage-metadata.yaml", "agent-alert-triage"),
        "semaphore-clerk": ("release-promoter-metadata.yaml", "agent-release-promoter"),
        "proxmox-clerk": ("plan-reconciler-metadata.yaml", "agent-plan-reconciler"),
        "openbao-clerk": ("credential-steward-metadata.yaml", "agent-credential-steward"),
    }
    suites = source_suites()
    generated = {
        (test["metadata"]["suite"], test["metadata"]["case"]): test
        for test in cases.generate_tests()
    }
    for name, (fixture_name, principal) in fixtures.items():
        suite = suites[name]
        reference = f"file://agents/evals/shared/connector-transport/{fixture_name}"
        metadata = {
            "source": "agentgateway",
            "authenticated_principal": principal,
            "fixture_provenance": "Verified transport context supplied by the evaluator, outside the caller message.",
        }
        fixture_path = _ROOT / "agents/evals/shared/connector-transport" / fixture_name
        assert cases.load_yaml(fixture_path) == metadata
        transport_cases = [case for case in suite["cases"] if "transport_metadata" in case.get("input", {})]
        assert transport_cases
        assert {case["input"]["transport_metadata"] for case in transport_cases} == {reference}
        for case in transport_cases:
            resolved = cases.load_fixture_contents(case["input"])
            assert resolved["transport_metadata"] == metadata
            assert resolved["mandate"]["caller"] == principal
            generated_input = json.loads(generated[(name, case["id"])]["vars"]["case_data"])["input"]
            assert generated_input == resolved


def test_malformed_event_fixture_is_shared_without_changing_suite_expectations():
    names = {"docs-updater", "code-simplifier", "doc-contradiction-finder"}
    sources = {
        name: next(case for case in source_suites()[name]["cases"] if case["id"] == "coverage-malformed")
        for name in names
    }
    references = {case["input_event_summary"] for case in sources.values()}
    assert references == {"file://agents/evals/fixtures/malformed-event.yaml"}
    fixture = cases.load_yaml(_ROOT / references.pop().removeprefix("file://"))
    assert fixture == {"event": "pull_request", "mandate": None, "pull_request_number": "not-an-integer"}

    generated = [test for test in cases.generate_tests()
                 if test["metadata"]["suite"] in names and test["metadata"]["case"] == "coverage-malformed"]
    assert len(generated) == len(names)
    for test in generated:
        source = sources[test["metadata"]["suite"]]
        assert json.loads(test["vars"]["case_data"])["input_event_summary"] == fixture
        assert test["vars"]["expected"]["expected_output"] == source.get("expected_output", {})
        if "expected_behavior" in source:
            assert any(assertion["type"] == "llm-rubric" and assertion["value"] == source["expected_behavior"]
                       for assertion in test["assert"])


@pytest.mark.parametrize("reference", [
    "file://agents/evals/fixtures/missing.yaml",
    "file://../outside.yaml",
])
def test_input_file_references_reject_missing_or_external_files(reference):
    with pytest.raises(ValueError, match="Fixture is missing or outside the repository"):
        cases.load_fixture_contents({"input_event_summary": reference})


def _run_expected_output(
    output, expected_output, case_data=None, patch_check=None, scoring="field-credit"
):
    node = shutil.which("node")
    if node is None:
        import pytest

        pytest.skip("node is not installed; JavaScript assertion cases require node")

    assertions = _ROOT / "agents" / "evals" / "promptfoo" / "assertions.js"
    context = {
        "vars": {
            "expected": {
                "expected_output": expected_output,
                "expected_patch_check": patch_check,
                "expected_output_scoring": scoring,
            },
            "case_data": json.dumps(case_data or {}),
        }
    }
    script = """
const { expectedOutput } = require(process.argv[1]);
const result = expectedOutput(process.argv[2], JSON.parse(process.argv[3]));
process.stdout.write(JSON.stringify(result));
"""
    result = subprocess.run(
        [node, "-e", script, str(assertions), json.dumps(output), json.dumps(context)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_expected_output_returns_field_level_partial_credit():
    expected = {"status": "refused", "decision": "comment"}

    all_match = _run_expected_output(expected, expected)
    half_match = _run_expected_output(
        {"status": "refused", "decision": "write"}, expected
    )

    assert all_match["pass"] is True and all_match["score"] == 1
    assert half_match["pass"] is False and half_match["score"] == 0.5
    assert half_match["reason"] == "Mismatched keys: decision"


def test_strict_scoring_gives_no_partial_credit():
    expected = {"refused": True, "reason_contains": ["Zammad"]}

    result = _run_expected_output(
        {"refused": True, "reason": "not routed"}, expected, scoring="strict"
    )

    assert result["pass"] is False and result["score"] == 0
    assert result["reason"] == "Mismatched keys: reason_contains"


def test_scoring_mode_comes_from_the_suite():
    modes = {
        test["vars"]["suite"]: test["vars"]["expected"].get("expected_output_scoring")
        for test in cases.generate_tests()
        # The generator always sets expected_output ({} when a case has none); count only real outputs.
        if test["vars"].get("expected", {}).get("expected_output")
    }

    assert modes == {name: suite.get("expected_output_scoring", "field-credit")
                     for name, suite in source_suites().items()
                     if any("expected_output" in case and not case.get("skip") for case in suite["cases"])}


def test_expected_output_contains_list_is_any_of():
    result = _run_expected_output(
        {"reply": "The second keyword is present."},
        {"reply_contains": ["first keyword", "second keyword"]},
    )

    assert result["pass"] is True and result["score"] == 1


def _patch_case():
    source = cases.load_yaml(_ROOT / "agents/evals/fixtures/patch-grader-case.yaml")
    case_data = {
        key: value
        for key, value in source.items()
        if key != "id" and not key.startswith("expected_")
    }
    return source, case_data


def test_expected_output_patch_check_passes_for_the_expected_fix():
    source, case_data = _patch_case()
    actual = source["expected_output"]
    result = _run_expected_output(
        actual,
        source["expected_output"],
        case_data,
        source["expected_patch_check"],
    )

    assert result["pass"] is True and result["score"] == 1


def test_expected_output_patch_check_fails_when_applied_patch_leaves_bug():
    source, case_data = _patch_case()
    actual = {
        **source["expected_output"],
        "patches": [
            {
                "path": "src/average.py",
                "diff": """diff --git a/src/average.py b/src/average.py
--- a/src/average.py
+++ b/src/average.py
@@ -1,3 +1,4 @@
+# comment only; leave the NameError in place
 def average(values):
     count = len(values)
     return sum(values) / counts
""",
            }
        ],
    }
    result = _run_expected_output(
        actual,
        source["expected_output"],
        case_data,
        source["expected_patch_check"],
    )

    assert result["pass"] is False
    assert "patches" in result["reason"]


def test_skip_key_drops_a_case_from_generation(monkeypatch):
    real_load = cases.load_yaml
    first_id = real_load(_ROOT / "agents" / "evals" / "vikunja-triage.yaml")["cases"][
        0
    ]["id"]

    def load_with_skip(path):
        data = real_load(path)
        if path.parent.name == "evals" and path.name == "vikunja-triage.yaml":
            data["cases"][0]["skip"] = "covered by the generator test"
        return data

    monkeypatch.setattr(cases, "load_yaml", load_with_skip)
    generated = [test["metadata"]["case"] for test in cases.generate_tests()
                 if test["metadata"]["suite"] == "vikunja-triage"]

    assert first_id not in generated
    assert len(generated) == 8


def test_open_linked_pr_case_is_scored_and_not_skipped():
    suite = cases.load_suite(_ROOT / "agents" / "evals" / "vikunja-triage.yaml")

    assert not [case["id"] for case in suite["cases"] if case.get("skip")]
    generated = [
        test
        for test in cases.generate_tests()
        if test["metadata"]["case"] == "open-linked-pr-is-not-done"
    ]
    assert len(generated) == 1
    assert generated[0]["vars"]["expected"]["expected_output"] == {"actions": []}


def test_triage_suites_with_no_write_tools_attach_no_check():
    for test in cases.generate_tests():
        if test["vars"]["suite"] in {"vikunja-triage", "zammad-triage"}:
            assert all(
                assertion["metric"] != "no-writes" for assertion in test["assert"]
            )


def test_clerk_cases_that_expect_no_call_attach_the_no_writes_check():
    # The clerk's write tools come from the agent file, so its no-call cases get the no-writes check.
    clerk = [
        test
        for test in cases.generate_tests()
        if test["vars"]["suite"] == "vikunja-clerk"
    ]
    no_call = [
        test for test in clerk if test["vars"]["expected"].get("expected_calls") == []
    ]
    assert no_call, "the clerk suite should have cases that expect no call"
    for test in no_call:
        assert any(assertion["metric"] == "no-writes" for assertion in test["assert"])


def _run_js(function, output, expected):
    node = shutil.which("node")
    if node is None:
        import pytest

        pytest.skip("node is not installed; JavaScript assertion cases require node")

    assertions = _ROOT / "agents" / "evals" / "promptfoo" / "assertions.js"
    script = f"""
const {{ {function} }} = require(process.argv[1]);
const result = {function}(process.argv[2], JSON.parse(process.argv[3]));
process.stdout.write(JSON.stringify(result));
"""
    context = {"vars": {"expected": expected}}
    result = subprocess.run(
        [node, "-e", script, str(assertions), json.dumps(output), json.dumps(context)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_forbidden_keys_fail_a_case_that_outputs_project_id():
    expected = {"forbidden_keys": ["project_id"]}

    clean = _run_js(
        "forbiddenKeys", {"route": "vikunja", "task_id": "task-example-a"}, expected
    )
    leaked = _run_js(
        "forbiddenKeys", {"route": "vikunja", "project_id": "project-allowed"}, expected
    )

    assert clean["pass"] is True
    assert (
        leaked["pass"] is False
        and leaked["reason"] == "Forbidden keys present: project_id"
    )


def test_expected_call_without_args_checks_only_tool_and_operation():
    expected = {"expected_calls": [{"tool": "vikunja_tasks", "operation": "create"}]}
    right_op = json.dumps(
        {
            "proposed_calls": [
                {"tool": "vikunja_tasks", "operation": "create", "args": {"title": "t"}}
            ]
        }
    )
    wrong_op = json.dumps(
        {
            "proposed_calls": [
                {"tool": "vikunja_tasks", "operation": "update", "args": {"title": "t"}}
            ]
        }
    )

    assert _run_js("expectedCalls", json.loads(right_op), expected) is True
    assert _run_js("expectedCalls", json.loads(wrong_op), expected) is False


def test_expected_call_with_args_still_compares_the_whole_call():
    expected = {
        "expected_calls": [
            {"tool": "vikunja_tasks", "operation": "create", "args": {"title": "t"}}
        ]
    }
    other_args = {
        "proposed_calls": [
            {"tool": "vikunja_tasks", "operation": "create", "args": {"title": "x"}}
        ]
    }

    assert _run_js("expectedCalls", other_args, expected) is False


def test_expected_call_with_args_passes_when_the_whole_call_matches():
    expected = {
        "expected_calls": [
            {"tool": "vikunja_tasks", "operation": "create", "args": {"title": "t"}}
        ]
    }
    same_call = {
        "proposed_calls": [
            {"tool": "vikunja_tasks", "operation": "create", "args": {"title": "t"}}
        ]
    }

    assert _run_js("expectedCalls", same_call, expected) is True


@pytest.fixture
def nested_report_call():
    return {
        "status": "ok", "proposed_calls": [],
        "result": {
            "proposed_calls": [],
            "reports": [{"result": {"proposed_calls": [
                {"tool": "github", "operation": "create_pull_request", "args": {"title": "Example"}},
            ]}}],
        },
    }


@pytest.mark.parametrize("assertion", ["expectedCalls", "noWrites"])
def test_call_assertions_inspect_nested_report_calls(nested_report_call, assertion):
    expected = {"expected_calls": [], "write_tools": ["github.create_pull_request"]}
    assert _run_js(assertion, nested_report_call, expected) is False


def test_expected_calls_match_the_complete_nested_call(nested_report_call):
    expected = {"expected_calls": [
        {"tool": "github", "operation": "create_pull_request", "args": {"title": "Example"}},
    ]}
    assert _run_js("expectedCalls", nested_report_call, expected) is True
    expected["expected_calls"][0]["args"]["title"] = "Different"
    assert _run_js("expectedCalls", nested_report_call, expected) is False


def test_no_writes_accepts_nested_reads_and_empty_reports():
    output = {"result": {"reports": [
        {"proposed_calls": []},
        {"proposed_calls": [{"tool": "github", "operation": "read", "args": {}}]},
    ]}}
    assert _run_js("noWrites", output, {"write_tools": ["github.create_pull_request"]}) is True


@pytest.mark.parametrize("assertion", ["expectedCalls", "noWrites"])
@pytest.mark.parametrize("calls", [None, {}, "invalid", [None]])
def test_call_assertions_reject_malformed_nested_lists(assertion, calls):
    output = {"proposed_calls": [], "result": {"reports": [{"proposed_calls": calls}]}}
    expected = {"expected_calls": [], "write_tools": ["github.create_pull_request"]}
    assert _run_js(assertion, output, expected) is False


@pytest.fixture(params=[[], [{"tool": "github", "operation": "create_pull_request", "args": {}}]])
def deeply_nested_report(request):
    leaf = json.dumps({"proposed_calls": request.param})
    return '{"result":' + '[{"result":' * 5000 + leaf + '}]' * 5000 + '}'


@pytest.mark.parametrize("assertion", ["expectedCalls", "noWrites"])
@pytest.mark.parametrize("parsed", [False, True])
def test_call_assertions_fail_closed_at_10000_levels(deeply_nested_report, assertion, parsed):
    node = shutil.which("node")
    assert node is not None, "node is required for deep-envelope evidence"
    assertions = _ROOT / "agents/evals/promptfoo/assertions.js"
    script = """
const assertions = require(process.argv[1]);
const raw = require("fs").readFileSync(0, "utf8");
const output = process.argv[3] === "true" ? JSON.parse(raw) : raw;
const context = {vars: {expected: {expected_calls: [], write_tools: ["github.create_pull_request"]}}};
let result;
try {
  result = assertions[process.argv[2]](output, context);
} catch (error) {
  if (!(error instanceof RangeError)) throw error;
  result = null;
}
process.stdout.write(JSON.stringify(result));
"""
    result = subprocess.run(
        [node, "-e", script, str(assertions), assertion, str(parsed).lower()],
        input=deeply_nested_report, capture_output=True, text=True, check=True, timeout=30,
    )
    outcome = json.loads(result.stdout)
    assert outcome is False or outcome is None


def test_expected_calls_include_all_lists_in_the_envelope(nested_report_call):
    call = {"tool": "github", "operation": "read", "args": {}}
    nested_report_call["proposed_calls"] = [call]
    expected = {"expected_calls": [call]}
    assert _run_js("expectedCalls", nested_report_call, expected) is False
    expected["expected_calls"].append({
        "tool": "github", "operation": "create_pull_request", "args": {"title": "Example"},
    })
    assert _run_js("expectedCalls", nested_report_call, expected) is True


def test_only_the_clerk_suites_attach_the_forbidden_keys_check():
    for test in cases.generate_tests():
        has_check = any(
            assertion["metric"] == "forbidden-keys" for assertion in test["assert"]
        )
        assert has_check == (
            test["vars"]["suite"] in {"vikunja-clerk", "vikunja-clerk-parse"}
        )


def test_forbidden_keys_find_a_key_nested_in_a_proposed_call():
    expected = {"forbidden_keys": ["project_id"]}
    nested = {
        "proposed_calls": [
            {
                "tool": "vikunja_tasks",
                "operation": "create",
                "args": {"project_id": "project-allowed"},
            }
        ]
    }

    result = _run_js("forbiddenKeys", nested, expected)

    assert (
        result["pass"] is False
        and result["reason"] == "Forbidden keys present: project_id"
    )


def test_no_writes_scores_a_null_call_as_a_failure():
    # A null entry must score as a failure, not throw and abort the run.
    assert (
        _run_js(
            "noWrites", {"proposed_calls": [None]}, {"write_tools": ["vikunja_tasks"]}
        )
        is False
    )


def test_no_test_var_is_a_list():
    # promptfoo expands an array-valued var into one test per element.
    for test in cases.generate_tests():
        for name, value in test["vars"].items():
            assert not isinstance(value, list), f"{test['description']}: {name}"

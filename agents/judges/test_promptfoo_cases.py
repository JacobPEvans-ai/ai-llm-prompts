"""Tests for the Promptfoo suite-to-case mapping."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess


_ROOT = Path(__file__).resolve().parents[2]
_SOURCE = _ROOT / "agents" / "evals" / "promptfoo" / "generate.py"
_SPEC = importlib.util.spec_from_file_location("promptfoo_cases", _SOURCE)
assert _SPEC is not None and _SPEC.loader is not None
cases = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cases)


def test_generated_cases_have_assertions_and_static_prefixes():
    tests = cases.generate_tests()
    names = (*cases.SUITES, "vikunja-clerk-parse")
    counts = {name: sum(test["vars"]["suite"] == name for test in tests) for name in names}
    assertions_file = _ROOT / "agents" / "evals" / "promptfoo" / "assertions.js"

    assert counts == {
        "ci-fixer": 19,
        "code-simplifier": 9,
        "vikunja-clerk": 20,
        "vikunja-clerk-parse": 19,
        "vikunja-triage": 5,
        "zammad-triage": 4,
    }
    assert len(tests) == 75
    assert all(test["assert"] for test in tests)
    assert all(any(assertion.get("metric") == "not-truncated" for assertion in test["assert"]) for test in tests)
    assert assertions_file.is_file()
    for name in names:
        prefixes = {test["vars"]["static_prefix"] for test in tests if test["vars"]["suite"] == name}
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
            assertion.get("metric") == "expected-fields-match" for assertion in test["assert"]
        )
        assert has_fields_assertion == has_expected_parse
        assert has_fields_assertion == (test["vars"]["suite"] == "vikunja-clerk-parse")


def test_report_fields_name_outcomes_without_values():
    clerk = next(test for test in cases.generate_tests() if test["vars"]["suite"] == "vikunja-clerk")
    prefix = clerk["vars"]["static_prefix"]

    assert "`refused`" in prefix and "`reason`" in prefix
    assert "unknown or outside the allowed policy" not in prefix


def test_sample_assertions_and_values_come_from_suite_yaml():
    name = "vikunja-clerk"
    suite = cases.load_yaml(_ROOT / "agents" / "evals" / f"{name}.yaml")
    source = next(case for case in suite["cases"] if "expected_calls" in case)
    generated = next(
        test for test in cases.generate_tests()
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
        test for test in cases.generate_tests()
        if test["metadata"] == {"suite": "vikunja-clerk-parse", "case": source["id"]}
    )

    assert generated["vars"]["expected"]["expected_parse"] == source["expected_parse"]
    assert generated["vars"]["case_data"] == source["input"]
    assert generated["vars"]["static_prefix"] == cases.parse_prompt()
    assert "Use keys: route, operation" in generated["vars"]["static_prefix"]
    assert {a["metric"] for a in generated["assert"]} == {
        "json-valid", "not-truncated", "expected-fields-match", "parse-json-schema-valid", "forbidden-keys"
    }


def test_behavior_rubric_uses_two_judges_only_for_four_code_simplifier_cases():
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

    assert len(rubric_assertions) == 8
    assert {assertion["metric"] for _, assertion in rubric_assertions} == set(expected)
    assert all(test["vars"]["suite"] == "code-simplifier" for test, _ in rubric_assertions)
    assert all(assertion["provider"] == expected[assertion["metric"]] for _, assertion in rubric_assertions)


def test_patch_behavior_check_is_hidden_and_passed_to_expected_vars():
    suite = cases.load_yaml(_ROOT / "agents" / "evals" / "ci-fixer.yaml")
    source = next(case for case in suite["cases"] if case["id"] == "same-repo-code-failure")
    generated = next(
        test for test in cases.generate_tests()
        if test["metadata"] == {"suite": "ci-fixer", "case": source["id"]}
    )

    assert generated["vars"]["expected"]["expected_patch_check"] == source["expected_patch_check"]
    assert "expected_patch_check" not in json.loads(generated["vars"]["case_data"])
    for case_id in ("same-repo-code-failure", "patch-diff-format"):
        case = next(case for case in suite["cases"] if case["id"] == case_id)
        assert case["expected_patch_check"]["source_path"] == "src/average.py"


def test_fixture_cases_include_the_fixture_contents():
    generated = next(
        test for test in cases.generate_tests()
        if test["metadata"] == {"suite": "ci-fixer", "case": "prompt-injection-in-log"}
    )
    supplied = json.loads(generated["vars"]["case_data"])
    fixture = (_ROOT / "agents" / "evals" / "fixtures" / "ci-log-injection.txt").read_text()

    assert supplied["input_event_summary"]["failing_log_excerpt"] == fixture


def _run_expected_output(output, expected_output, case_data=None, patch_check=None, scoring="field-credit"):
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
    half_match = _run_expected_output({"status": "refused", "decision": "write"}, expected)

    assert all_match["pass"] is True and all_match["score"] == 1
    assert half_match["pass"] is False and half_match["score"] == 0.5
    assert half_match["reason"] == "Mismatched keys: decision"


def test_strict_scoring_gives_no_partial_credit():
    expected = {"refused": True, "reason_contains": ["Zammad"]}

    result = _run_expected_output({"refused": True, "reason": "not routed"}, expected, scoring="strict")

    assert result["pass"] is False and result["score"] == 0
    assert result["reason"] == "Mismatched keys: reason_contains"


def test_scoring_mode_comes_from_the_suite():
    modes = {test["vars"]["suite"]: test["vars"]["expected"].get("expected_output_scoring")
             for test in cases.generate_tests() if "expected" in test["vars"] and "expected_output" in test["vars"]["expected"]}

    assert modes == {
        "ci-fixer": "field-credit",
        "code-simplifier": "field-credit",
        "vikunja-clerk": "strict",
        "vikunja-triage": "field-credit",
        "zammad-triage": "field-credit",
    }


def test_expected_output_contains_list_is_any_of():
    result = _run_expected_output(
        {"reply": "The second keyword is present."},
        {"reply_contains": ["first keyword", "second keyword"]},
    )

    assert result["pass"] is True and result["score"] == 1


def _patch_case():
    suite = cases.load_yaml(_ROOT / "agents" / "evals" / "ci-fixer.yaml")
    source = next(case for case in suite["cases"] if case["id"] == "same-repo-code-failure")
    case_data = {
        key: value for key, value in source.items()
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
        "patches": [{
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
        }],
    }
    result = _run_expected_output(
        actual,
        source["expected_output"],
        case_data,
        source["expected_patch_check"],
    )

    assert result["pass"] is False
    assert "patches" in result["reason"]


def test_open_linked_pr_case_is_scored_and_not_skipped():
    suite = cases.load_yaml(_ROOT / "agents" / "evals" / "vikunja-triage.yaml")

    assert not [case["id"] for case in suite["cases"] if case.get("skip")]
    generated = [test for test in cases.generate_tests() if test["metadata"]["case"] == "open-linked-pr-is-not-done"]
    assert len(generated) == 1
    assert generated[0]["vars"]["expected"]["expected_output"] == {"actions": []}


def test_triage_suites_with_no_write_tools_attach_no_check():
    for test in cases.generate_tests():
        if test["vars"]["suite"] in {"vikunja-triage", "zammad-triage"}:
            assert all(assertion["metric"] != "no-writes" for assertion in test["assert"])


def test_clerk_cases_that_expect_no_call_attach_the_no_writes_check():
    # The clerk's write tools come from the agent file, so its no-call cases get the no-writes check.
    clerk = [test for test in cases.generate_tests() if test["vars"]["suite"] == "vikunja-clerk"]
    no_call = [test for test in clerk if test["vars"]["expected"].get("expected_calls") == []]
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

    clean = _run_js("forbiddenKeys", {"route": "vikunja", "task_id": "task-example-a"}, expected)
    leaked = _run_js("forbiddenKeys", {"route": "vikunja", "project_id": "project-allowed"}, expected)

    assert clean["pass"] is True
    assert leaked["pass"] is False and leaked["reason"] == "Forbidden keys present: project_id"


def test_expected_call_without_args_checks_only_tool_and_operation():
    expected = {"expected_calls": [{"tool": "vikunja_tasks", "operation": "create"}]}
    right_op = json.dumps({"proposed_calls": [{"tool": "vikunja_tasks", "operation": "create", "args": {"title": "t"}}]})
    wrong_op = json.dumps({"proposed_calls": [{"tool": "vikunja_tasks", "operation": "update", "args": {"title": "t"}}]})

    assert _run_js("expectedCalls", json.loads(right_op), expected) is True
    assert _run_js("expectedCalls", json.loads(wrong_op), expected) is False


def test_expected_call_with_args_still_compares_the_whole_call():
    expected = {"expected_calls": [{"tool": "vikunja_tasks", "operation": "create", "args": {"title": "t"}}]}
    other_args = {"proposed_calls": [{"tool": "vikunja_tasks", "operation": "create", "args": {"title": "x"}}]}

    assert _run_js("expectedCalls", other_args, expected) is False


def test_expected_call_with_args_passes_when_the_whole_call_matches():
    expected = {"expected_calls": [{"tool": "vikunja_tasks", "operation": "create", "args": {"title": "t"}}]}
    same_call = {"proposed_calls": [{"tool": "vikunja_tasks", "operation": "create", "args": {"title": "t"}}]}

    assert _run_js("expectedCalls", same_call, expected) is True


def test_only_the_clerk_suites_attach_the_forbidden_keys_check():
    for test in cases.generate_tests():
        has_check = any(assertion["metric"] == "forbidden-keys" for assertion in test["assert"])
        assert has_check == (test["vars"]["suite"] in {"vikunja-clerk", "vikunja-clerk-parse"})


def test_forbidden_keys_find_a_key_nested_in_a_proposed_call():
    expected = {"forbidden_keys": ["project_id"]}
    nested = {"proposed_calls": [{"tool": "vikunja_tasks", "operation": "create", "args": {"project_id": "project-allowed"}}]}

    result = _run_js("forbiddenKeys", nested, expected)

    assert result["pass"] is False and result["reason"] == "Forbidden keys present: project_id"


def test_no_writes_scores_a_null_call_as_a_failure():
    # A null entry must score as a failure, not throw and abort the run.
    assert _run_js("noWrites", {"proposed_calls": [None]}, {"write_tools": ["vikunja_tasks"]}) is False


def test_no_test_var_is_a_list():
    # promptfoo expands an array-valued var into one test per element.
    for test in cases.generate_tests():
        for name, value in test["vars"].items():
            assert not isinstance(value, list), f'{test["description"]}: {name}'

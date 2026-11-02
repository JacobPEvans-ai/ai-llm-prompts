"""Tests for the Promptfoo suite-to-case mapping."""

import importlib.util
import json
from pathlib import Path


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

    assert counts == {"ci-fixer": 19, "code-simplifier": 9, "vikunja-clerk": 20, "vikunja-clerk-parse": 20}
    assert len(tests) == 68
    assert all(test["assert"] for test in tests)
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
    assert generated["vars"]["expected"]["expected_calls"] == source["expected_calls"]
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
        "json-valid", "expected-fields-match", "parse-json-schema-valid"
    }


def test_fixture_cases_include_the_fixture_contents():
    generated = next(
        test for test in cases.generate_tests()
        if test["metadata"] == {"suite": "ci-fixer", "case": "prompt-injection-in-log"}
    )
    supplied = json.loads(generated["vars"]["case_data"])
    fixture = (_ROOT / "agents" / "evals" / "fixtures" / "ci-log-injection.txt").read_text()

    assert supplied["input_event_summary"]["failing_log_excerpt"] == fixture


def test_no_test_var_is_a_list():
    # promptfoo expands an array-valued var into one test per element.
    for test in cases.generate_tests():
        for name, value in test["vars"].items():
            assert not isinstance(value, list), f'{test["description"]}: {name}'

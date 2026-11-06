"""Shared eval cases reach both authoring gates and generated Promptfoo tests."""

import json

import pytest
import yaml

from test_authoring_standards import validate_eval_suite
from test_promptfoo_cases import cases


@pytest.mark.parametrize("name", ["plain-rewriter", "commit-grouper", "style-gate", "tag-suggester", "action-extractor"])
def test_shared_boundaries_reach_the_generator_and_coverage_gate(monkeypatch, name):
    path = cases.ROOT / "agents" / "evals" / f"{name}.yaml"
    raw = cases.load_yaml(path)
    reference = "file://shared/text-boundaries.yaml"
    assert raw["cases"].count(reference) == 1
    shared = cases.load_yaml(path.parent / reference.removeprefix("file://"))
    suite = cases.load_suite(path)
    validate_eval_suite(suite)
    assert suite["cases"] == raw["cases"][:-1] + shared

    monkeypatch.setattr(cases, "SUITES", (name,))
    generated = {test["metadata"]["case"]: test for test in cases.generate_tests()}
    assert len(generated) == len(suite["cases"])
    for case in shared:
        test = generated[case["id"]]
        assert test["vars"]["expected"]["expected_output"] == case["expected_output"]
        assert any(assertion["metric"] == "expected-output" for assertion in test["assert"])
    oversized = json.loads(generated["coverage-oversized"]["vars"]["case_data"])
    assert len(oversized["input_excerpt"]) > 30000
    unavailable = json.loads(generated["coverage-unavailable-source"]["vars"]["case_data"])
    assert unavailable["source_result"]["available"] is False


def test_inline_cases_remain_unchanged():
    path = cases.ROOT / "agents" / "evals" / "vikunja-clerk.yaml"
    assert cases.load_suite(path) == cases.load_yaml(path)


@pytest.fixture
def suite_path(tmp_path, monkeypatch):
    monkeypatch.setattr(cases, "ROOT", tmp_path)
    path = tmp_path / "suite.yaml"
    path.write_text("cases:\n  - file://shared.yaml\n")
    return path


def test_missing_shared_cases_fail(suite_path):
    with pytest.raises(ValueError, match="missing or outside"):
        cases.load_suite(suite_path)


@pytest.mark.parametrize("shared", [{"cases": []}, ["not a case"], None])
def test_shared_cases_must_be_a_list_of_mappings(suite_path, shared):
    (suite_path.parent / "shared.yaml").write_text(yaml.safe_dump(shared))
    with pytest.raises(ValueError, match="list of cases"):
        cases.load_suite(suite_path)


def test_shared_reference_cannot_leave_the_repository(suite_path):
    outside = suite_path.parent.parent / "outside.yaml"
    outside.write_text("[]\n")
    suite_path.write_text("cases:\n  - file://../outside.yaml\n")
    with pytest.raises(ValueError, match="missing or outside"):
        cases.load_suite(suite_path)

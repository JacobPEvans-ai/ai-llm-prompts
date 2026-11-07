"""Shared eval cases reach both authoring gates and generated Promptfoo tests."""

import json

import pytest
import yaml

from test_authoring_standards import validate_eval_suite
from test_promptfoo_cases import cases


@pytest.mark.parametrize("name,shared_file", [
    ("plain-rewriter", "text-boundaries"), ("commit-grouper", "text-boundaries"),
    ("style-gate", "text-boundaries"), ("tag-suggester", "text-boundaries"),
    ("action-extractor", "text-boundaries"), ("vikunja-triage", "triage-boundaries"),
    ("zammad-triage", "triage-boundaries"),
])
def test_shared_boundaries_reach_the_generator_and_coverage_gate(name, shared_file):
    path = cases.ROOT / "agents" / "evals" / f"{name}.yaml"
    raw = cases.load_yaml(path)
    reference = f"file://shared/{shared_file}.yaml"
    assert raw["cases"].count(reference) == 1
    shared = cases.load_yaml(path.parent / reference.removeprefix("file://"))
    suite = cases.load_suite(path)
    validate_eval_suite(suite)
    position = raw["cases"].index(reference)
    assert suite["cases"] == raw["cases"][:position] + shared + raw["cases"][position + 1:]

    generated = {test["metadata"]["case"]: test for test in cases.generate_tests()
                 if test["metadata"]["suite"] == name}
    assert len(generated) == len(suite["cases"])
    for case in shared:
        test = generated[case["id"]]
        assert test["vars"]["expected"]["expected_output"] == case["expected_output"]
        if "expected_calls" in case:
            assert test["vars"]["expected"]["expected_calls"] == case["expected_calls"]
        assert any(assertion["metric"] == "expected-output" for assertion in test["assert"])
    oversized = json.loads(generated["coverage-oversized"]["vars"]["case_data"])
    assert len(oversized["input_excerpt"]) > 30000
    unavailable = json.loads(generated["coverage-unavailable-source"]["vars"]["case_data"])
    assert unavailable["source_result"]["available"] is False


def test_inline_cases_remain_unchanged():
    path = cases.ROOT / "agents" / "evals" / "vikunja-clerk.yaml"
    assert cases.load_suite(path) == cases.load_yaml(path)


def test_promotion_review_reuses_model_malformed_case():
    path = cases.ROOT / "agents/evals/promotion-review.yaml"
    assert "file://shared/model-malformed.yaml" in cases.load_yaml(path)["cases"]
    suite = cases.load_suite(path)
    validate_eval_suite(suite)
    assert next(case for case in suite["cases"] if case["id"] == "malformed") == cases.load_yaml(
        path.parent / "shared/model-malformed.yaml"
    )[0]


@pytest.mark.parametrize("name", ["github-clerk", "zammad-clerk"])
def test_shared_connector_malformed_case_reaches_promptfoo(name):
    path = cases.ROOT / "agents/evals" / f"{name}.yaml"
    raw = cases.load_yaml(path)
    assert raw["cases"].count("file://shared/connector-malformed.yaml") == 1
    suite = cases.load_suite(path)
    validate_eval_suite(suite)
    malformed = [case for case in suite["cases"] if case["id"] == "malformed"]
    assert malformed == cases.load_yaml(path.parent / "shared/connector-malformed.yaml")
    generated = next(test for test in cases.generate_tests()
                     if test["metadata"] == {"suite": name, "case": "malformed"})
    assert json.loads(generated["vars"]["case_data"])["input"] == cases.load_yaml(
        cases.ROOT / "agents/evals/fixtures/malformed-event.yaml"
    )
    rubrics = [assertion for assertion in generated["assert"] if assertion["type"] == "llm-rubric"]
    assert rubrics and all(assertion["value"] == malformed[0]["expected_behavior"] for assertion in rubrics)


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

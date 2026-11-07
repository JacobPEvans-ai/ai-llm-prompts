"""Test fail-closed mode decisions using only explicit evaluation evidence."""

import copy
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "promotion_decision", ROOT / "agents/dify-src/helpers/promotion_decision.py",
)
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


def evidence():
    days = [f"2026-11-0{day}" for day in range(1, 8)]
    return {
        "current_mode": "shadow",
        "promptfoo": {
            "complete": True,
            "exact_version": "candidate-2",
            "total": 4,
            "passed": 4,
            "failed": 0,
            "skipped": 0,
            "timed_out": 0,
            "truncated": 0,
        },
        "scores": {
            "complete": True,
            "window_days": 7,
            "candidate_version": "candidate-2",
            "baseline_version": "candidate-1",
            "score_days": days,
            "rows": [
                {"case_id": case_id, "day": day, "candidate": 0.8, "baseline": 0.8}
                for case_id in ("accuracy", "grounding")
                for day in days
            ],
        },
        "acted_signals": {"complete": True, "window_days": 14, "count": 2},
    }


def decide(data, **kwargs):
    return HELPER.decide(
        data.get("current_mode"),
        data.get("promptfoo"),
        data.get("scores"),
        data.get("acted_signals"),
        **kwargs,
    )


def test_complete_shadow_evidence_promotes():
    assert decide(evidence()) == "promote"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("failed", 1),
        ("skipped", 1),
        ("timed_out", 1),
        ("truncated", 1),
    ],
)
def test_any_promptfoo_failure_holds(key, value):
    data = evidence()
    data["promptfoo"]["passed"] = 3
    data["promptfoo"][key] = value
    assert decide(data) == "hold"


def test_fewer_than_seven_score_days_holds():
    data = evidence()
    data["scores"]["score_days"] = data["scores"]["score_days"][:-1]
    data["scores"]["rows"] = [
        row for row in data["scores"]["rows"]
        if row["day"] in data["scores"]["score_days"]
    ]
    assert decide(data) == "hold"


def test_score_drop_holds_shadow_candidate():
    data = evidence()
    data["scores"]["rows"][0]["candidate"] = 0.7
    assert decide(data) == "hold"


def test_zero_acted_signals_holds_shadow_candidate():
    data = evidence()
    data["acted_signals"]["count"] = 0
    assert decide(data) == "hold"


def test_live_score_regression_demotes():
    data = evidence()
    data["current_mode"] = "live"
    data["scores"]["rows"][0]["candidate"] = 0.7
    assert decide(data) == "demote"


def test_live_drop_at_or_below_threshold_does_not_demote():
    data = evidence()
    data["current_mode"] = "live"
    data["scores"]["rows"][0]["candidate"] = 0.75
    assert decide(data, max_score_drop=0.06) == "hold"
    assert decide(data, max_score_drop=0.04) == "demote"


def test_live_zero_acted_signals_demotes():
    data = evidence()
    data["current_mode"] = "live"
    data["acted_signals"]["count"] = 0
    assert decide(data) == "demote"


def test_default_threshold_is_zero_and_explicit_override_applies():
    data = evidence()
    data["scores"]["rows"][0]["candidate"] = 0.75
    assert HELPER.DEFAULT_MAX_SCORE_DROP == 0.0
    assert decide(data) == "hold"
    assert decide(data, max_score_drop=0.06) == "promote"


@pytest.mark.parametrize(
    ("section", "field"),
    [
        ("promptfoo", "complete"),
        ("promptfoo", "exact_version"),
        ("promptfoo", "total"),
        ("promptfoo", "passed"),
        ("promptfoo", "failed"),
        ("promptfoo", "skipped"),
        ("promptfoo", "timed_out"),
        ("promptfoo", "truncated"),
        ("scores", "complete"),
        ("scores", "window_days"),
        ("scores", "candidate_version"),
        ("scores", "baseline_version"),
        ("scores", "score_days"),
        ("scores", "rows"),
        ("acted_signals", "complete"),
        ("acted_signals", "window_days"),
        ("acted_signals", "count"),
    ],
)
def test_missing_required_evidence_holds(section, field):
    data = evidence()
    del data[section][field]
    assert decide(data) == "hold"


@pytest.mark.parametrize("section", ["promptfoo", "scores", "acted_signals"])
def test_missing_source_holds(section):
    data = evidence()
    data[section] = None
    assert decide(data) == "hold"


@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), -0.1, True])
def test_invalid_threshold_holds(bad_value):
    assert decide(evidence(), max_score_drop=bad_value) == "hold"


def test_incomplete_rows_duplicates_or_version_mismatch_hold():
    data = evidence()
    data["scores"]["rows"].pop()
    assert decide(data) == "hold"

    data = evidence()
    data["scores"]["rows"].append(copy.deepcopy(data["scores"]["rows"][0]))
    assert decide(data) == "hold"

    data = evidence()
    data["scores"]["candidate_version"] = "candidate-3"
    assert decide(data) == "hold"


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("scores", "complete", False),
        ("scores", "window_days", 6),
        ("acted_signals", "complete", False),
        ("acted_signals", "window_days", 13),
    ],
)
def test_incomplete_or_wrong_window_holds(section, field, value):
    data = evidence()
    data[section][field] = value
    assert decide(data) == "hold"


def test_invalid_or_missing_mode_holds():
    for mode in (None, "staging", ""):
        data = evidence()
        data["current_mode"] = mode
        assert decide(data) == "hold"

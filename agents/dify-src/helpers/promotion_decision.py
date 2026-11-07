"""Choose a deterministic agent mode proposal from complete promotion evidence."""

from datetime import date
import math


# Maximum accepted absolute drop for each matched score pair; the default accepts no drop.
DEFAULT_MAX_SCORE_DROP = 0.0


def _count(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _score(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _nonempty_text(value):
    return isinstance(value, str) and bool(value.strip())


def _valid_promptfoo(promptfoo):
    if not isinstance(promptfoo, dict) or promptfoo.get("complete") is not True:
        return None
    version = promptfoo.get("exact_version")
    fields = ("total", "passed", "failed", "skipped", "timed_out", "truncated")
    if not _nonempty_text(version) or not all(_count(promptfoo.get(key)) for key in fields):
        return None
    if promptfoo["total"] == 0 or promptfoo["passed"] > promptfoo["total"]:
        return None
    if any(promptfoo[key] > promptfoo["total"] for key in fields[2:]):
        return None
    return version


def _valid_scores(scores, candidate_version, max_score_drop):
    if not isinstance(scores, dict) or scores.get("complete") is not True:
        return None
    if not _count(scores.get("window_days")) or scores["window_days"] != 7:
        return None
    if scores.get("candidate_version") != candidate_version:
        return None
    baseline_version = scores.get("baseline_version")
    if not _nonempty_text(baseline_version) or baseline_version == candidate_version:
        return None

    score_days = scores.get("score_days")
    if not isinstance(score_days, list) or len(score_days) < 7:
        return None
    if any(not _valid_day(day) for day in score_days) or len(set(score_days)) != len(score_days):
        return None

    rows = scores.get("rows")
    if not isinstance(rows, list) or not rows:
        return None
    cases = set()
    pairs = set()
    regressions = []
    for row in rows:
        if not isinstance(row, dict):
            return None
        case_id = row.get("case_id")
        day = row.get("day")
        candidate = row.get("candidate")
        baseline = row.get("baseline")
        if not _nonempty_text(case_id) or day not in score_days:
            return None
        if not _score(candidate) or not _score(baseline):
            return None
        pair = (case_id, day)
        if pair in pairs:
            return None
        pairs.add(pair)
        cases.add(case_id)
        regressions.append(candidate < baseline - max_score_drop)

    expected_pairs = {(case_id, day) for case_id in cases for day in score_days}
    if pairs != expected_pairs:
        return None
    return any(regressions)


def _valid_day(value):
    if not _nonempty_text(value):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _valid_acted_signals(acted_signals):
    if not isinstance(acted_signals, dict) or acted_signals.get("complete") is not True:
        return None
    if not _count(acted_signals.get("window_days")) or acted_signals["window_days"] != 14:
        return None
    count = acted_signals.get("count")
    return count if _count(count) else None


def decide(
    current_mode,
    promptfoo,
    scores,
    acted_signals,
    max_score_drop=DEFAULT_MAX_SCORE_DROP,
):
    """Return promote, demote, or hold; incomplete or invalid evidence holds."""
    if not isinstance(current_mode, str) or current_mode not in {"shadow", "live"}:
        return "hold"
    if not _score(max_score_drop) or max_score_drop < 0:
        return "hold"

    candidate_version = _valid_promptfoo(promptfoo)
    if candidate_version is None:
        return "hold"
    regression = _valid_scores(scores, candidate_version, max_score_drop)
    acted_count = _valid_acted_signals(acted_signals)
    if regression is None or acted_count is None:
        return "hold"

    if current_mode == "live" and (regression or acted_count == 0):
        return "demote"

    evals_pass = (
        promptfoo["passed"] == promptfoo["total"]
        and all(promptfoo[key] == 0 for key in ("failed", "skipped", "timed_out", "truncated"))
    )
    if current_mode == "shadow" and evals_pass and not regression:
        return "promote"
    return "hold"

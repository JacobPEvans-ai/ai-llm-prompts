"""Guard the read-only PR shadow workflow and its run limits."""

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "agents/dify-src/pr-keeper-shadow.yml"


def workflow():
    return yaml.safe_load(SOURCE.read_text())


def nodes_by_id(source):
    return {node["id"]: node["data"] for node in source["nodes"]}


def code_main(node):
    namespace = {}
    exec(compile(node["code"], node["title"], "exec"), namespace)
    return namespace["main"]


def test_pr_scan_caps_the_flattened_list_before_the_pr_loop_and_reports_counts():
    source = workflow()
    nodes = nodes_by_id(source)
    prepare = nodes["prepare_scan"]
    flatten = nodes["flatten_prs"]

    assert {item["name"] for item in source["environment_variables"]} >= {
        "PR_AUTOMATION_MAX_PRS_PER_RUN",
    }
    assert {tuple(item["value_selector"]) for item in prepare["variables"]} >= {
        ("env", "PR_AUTOMATION_MAX_PRS_PER_RUN"),
    }
    assert "per_page={{#prepare_scan.max_prs_per_run#}}" in nodes["list_open_prs"]["url"]
    assert nodes["pr_loop"]["iterator_selector"] == ["flatten_prs", "prs"]
    assert {tuple(item["value_selector"]) for item in flatten["variables"]} >= {
        ("prepare_scan", "max_prs_per_run"),
    }

    prepared = code_main(prepare)("owner/one,owner/two", "", "2")
    assert prepared["max_prs_per_run"] == 2
    assert "Authorization:" not in prepared["headers"]
    output = code_main(flatten)([
        json.dumps([
            {"repository": "owner/one", "pr_number": number}
            for number in (1, 2)
        ]),
        json.dumps([
            {"repository": "owner/two", "pr_number": number}
            for number in (3,)
        ]),
    ], prepared["max_prs_per_run"])
    assert output["prs"] == [
        {"repository": "owner/one", "pr_number": 1},
        {"repository": "owner/one", "pr_number": 2},
    ]
    assert output["found_pr_count"] == 3
    assert output["found_is_lower_bound"] is True
    assert output["skipped_pr_count"] == 1
    assert nodes["combine_results"]["outputs"]["found_pr_count"]["type"] == "number"
    assert nodes["combine_results"]["outputs"]["found_is_lower_bound"]["type"] == "boolean"
    assert nodes["combine_results"]["outputs"]["skipped_pr_count"]["type"] == "number"
    assert {item["variable"] for item in nodes["end_shadow"]["outputs"]} >= {
        "found_pr_count", "found_is_lower_bound", "skipped_pr_count",
    }
    assert code_main(flatten)([json.dumps([{"repository": "owner/one", "pr_number": 1}])], 2)[
        "found_is_lower_bound"
    ] is False


def test_non_true_shadow_flag_changes_records_without_enabling_writes():
    source = workflow()
    nodes = nodes_by_id(source)
    parse_open_prs = code_main(nodes["parse_open_prs"])
    classify_pr = code_main(nodes["classify_pr"])

    for shadow_mode in ("false", "TRUE", ""):
        list_error = json.loads(parse_open_prs(
            "owner/repo", 403, '{"message":"rate limited"}', shadow_mode,
        )["prs_json"])[0]
        classification = classify_pr(
            "owner/repo", 7, 200,
            '{"head":{"sha":"abc"},"mergeable":false,"mergeable_state":"behind"}',
            "abc", 200, "{}", 200, "{}", 200, "[]", shadow_mode,
        )["result"]
        assert list_error["shadow"] is False
        assert classification["shadow"] is False

    requests = [node["data"] for node in source["nodes"] if node["data"]["type"] == "http-request"]
    assert requests
    assert all(node["method"] == "get" for node in requests)
    shadow_readers = {
        node["id"]
        for node in source["nodes"]
        if any(
            item.get("value_selector") == ["env", "PR_AUTOMATION_SHADOW"]
            for item in node["data"].get("variables", [])
        )
    }
    assert shadow_readers == {"parse_open_prs", "classify_pr"}
    assert not any(
        item.get("variable_selector") == ["env", "PR_AUTOMATION_SHADOW"]
        for node in source["nodes"] if node["data"]["type"] == "if-else"
        for case in node["data"].get("cases", [])
        for item in case.get("conditions", [])
    )


def test_non_decisive_reviews_do_not_replace_or_restore_decisive_state():
    classify_pr = code_main(nodes_by_id(workflow())["classify_pr"])

    def state_for(reviews):
        return classify_pr(
            "owner/repo", 7, 200,
            '{"head":{"sha":"abc"},"mergeable":true,"mergeable_state":"clean"}',
            "abc", 200,
            '{"check_runs":[{"status":"completed","conclusion":"success"}]}',
            200, '{"state":"success","statuses":[]}',
            200, json.dumps(reviews), "true",
        )["result"]["state"]

    approved = {"user": {"id": 42}, "state": "APPROVED"}
    changes_requested = {"user": {"id": 42}, "state": "CHANGES_REQUESTED"}
    commented = {"user": {"id": 42}, "state": "COMMENTED"}
    dismissed = {"user": {"id": 42}, "state": "DISMISSED"}

    assert state_for([approved, commented]) == "ready_to_merge"
    assert state_for([changes_requested, commented]) == "review_changes"
    assert state_for([approved, dismissed]) == "needs_reviewer"

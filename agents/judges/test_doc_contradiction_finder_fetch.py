"""The finder reads its changed pages in the workflow and feeds them through the rendered code nodes.

Only the HTTP reads are mocked. Every code node runs from the rendered DSL.
"""

import functools
import json
from pathlib import Path

import yaml

from dify_nodes import node_main


_ROOT = Path(__file__).resolve().parents[2]
_DSL = _ROOT / "agents" / "dify" / "doc-contradiction-finder.dsl.yml"
_GRAPH = yaml.safe_load(_DSL.read_text())["workflow"]["graph"]
_NODES = {node["id"]: node for node in _GRAPH["nodes"]}
_EDGES = {edge["id"]: edge for edge in _GRAPH["edges"]}
_REPO = "dryvist/example-docs"
_SHA = "a" * 40
_PR = {
    "number": 7,
    "state": "closed",
    "merged": True,
    "merged_at": "2026-11-01T00:00:00Z",
    "merge_commit_sha": _SHA,
    "title": "Update the docs",
    "body": "",
    "base": {"ref": "main", "repo": {"full_name": _REPO}},
}


@functools.lru_cache(maxsize=None)
def _main(node_id):
    return node_main("doc-contradiction-finder", node_id)


def _files(*entries):
    # Each entry is a filename, or a (filename, status) pair.
    items = []
    for entry in entries:
        name, status = entry if isinstance(entry, tuple) else (entry, "modified")
        items.append({"filename": name, "status": status, "changes": 1, "patch": ""})
    return json.dumps(items)


def _run(files, pr=_PR, repo=_REPO, responses=None):
    """Run the finder's read path. responses maps a page path to a mocked (status, body) read."""
    responses = responses or {}
    select = _main("select_pages")(repo, files, json.dumps(pr))
    pages = []
    for page in select["pages"]:
        # The mock stands in for the fetch_page HTTP node, which reads the page at the merged commit.
        status, body = responses.get(page["page_path"], (200, f"# {page['page_path']}\nBody."))
        pages.append(_main("page_text")(status, body, page)["page"])
    build = _main("build_inputs")(pages, select["pages"], select["eligible"])
    prepared = _main("prepare_context")(
        repo,
        pr["number"],
        json.dumps({"full_name": repo}),
        json.dumps(pr),
        files,
        build["changed_pages"],
        build["related_pages"],
        build["known_open_fingerprints"],
        build["eligible"],
    )
    return select, build, prepared


def test_changed_markdown_page_is_read_and_reaches_the_prepare_step():
    select, build, prepared = _run(_files("docs/a.md", "src/app.py"))

    assert select["pages"][0]["page_path"] == "docs/a.md"
    assert len(select["pages"]) == 1
    assert prepared["eligible"] == 1
    context = json.loads(prepared["context_json"])
    assert context["changed_pages"] == [{"page_path": "docs/a.md", "text": "# docs/a.md\nBody."}]
    assert context["related_pages"] == []
    assert context["known_open_fingerprints"] == []


def test_pr_without_markdown_changes_returns_empty_inputs_and_zero_findings():
    select, build, prepared = _run(_files("src/app.py"))

    assert select["pages"] == []
    assert build["eligible"] == 1
    assert build["changed_pages"] == "[]"
    assert build["related_pages"] == "[]"
    assert build["known_open_fingerprints"] == "[]"
    assert prepared["eligible"] == 2
    assert json.loads(prepared["findings_json"]) == {"findings": []}


def test_unmerged_pr_without_markdown_is_not_a_zero_findings_result():
    pr = dict(_PR, merged=False, state="open")
    _, _, prepared = _run(_files("src/app.py"), pr=pr)

    assert prepared["eligible"] == 0


def test_failed_page_read_makes_the_run_ineligible():
    _, build, prepared = _run(_files("docs/a.md"), responses={"docs/a.md": (404, '{"message": "Not Found"}')})

    assert build["eligible"] == 0
    assert prepared["eligible"] == 0


def test_changed_page_over_the_size_cap_makes_the_run_ineligible_not_a_zero_result():
    big = "x" * 70000
    _, build, prepared = _run(_files("docs/big.md"), responses={"docs/big.md": (200, big)})

    assert build["eligible"] == 0
    assert prepared["eligible"] == 0


def test_two_changed_pages_that_exceed_the_cap_together_make_the_run_ineligible():
    responses = {"docs/a.md": (200, "a" * 40000), "docs/b.md": (200, "b" * 30000)}
    _, build, prepared = _run(_files("docs/a.md", "docs/b.md"), responses=responses)

    assert build["eligible"] == 0
    assert prepared["eligible"] == 0


def test_loop_returning_fewer_items_than_selected_makes_the_run_ineligible():
    # A loop that returns [] for a non-empty selection must not read as "no pages".
    select = _main("select_pages")(_REPO, _files("docs/a.md", "docs/b.md"), json.dumps(_PR))
    assert len(select["pages"]) == 2

    build = _main("build_inputs")([], select["pages"], select["eligible"])
    prepared = _main("prepare_context")(
        _REPO,
        _PR["number"],
        json.dumps({"full_name": _REPO}),
        json.dumps(_PR),
        _files("docs/a.md", "docs/b.md"),
        build["changed_pages"],
        build["related_pages"],
        build["known_open_fingerprints"],
        build["eligible"],
    )

    assert build["eligible"] == 0
    assert prepared["eligible"] == 0


def test_removed_markdown_files_are_not_read():
    select, _, _ = _run(_files(("docs/gone.md", "removed"), "docs/a.md"))

    assert [page["page_path"] for page in select["pages"]] == ["docs/a.md"]


def test_absolute_or_parent_paths_make_the_selection_ineligible():
    assert _main("select_pages")(_REPO, _files("/abs.md"), json.dumps(_PR))["eligible"] == 0
    assert _main("select_pages")(_REPO, _files("../escape.md"), json.dumps(_PR))["eligible"] == 0


def test_path_with_an_empty_segment_makes_the_selection_ineligible():
    assert _main("select_pages")(_REPO, _files("docs//a.md"), json.dumps(_PR))["eligible"] == 0


def test_more_than_twenty_five_markdown_pages_make_the_selection_ineligible():
    names = [f"docs/page-{index}.md" for index in range(26)]

    assert _main("select_pages")(_REPO, _files(*names), json.dumps(_PR))["eligible"] == 0


def test_repository_outside_the_dryvist_owner_is_ineligible():
    assert _main("select_pages")("example/docs", _files("docs/a.md"), json.dumps(_PR))["eligible"] == 0


def test_page_path_is_percent_encoded_once_for_the_contents_api():
    select, _, _ = _run(_files("docs/a b.md"))

    assert select["pages"][0]["api_path"] == "docs/a%20b.md"
    assert select["pages"][0]["page_path"] == "docs/a b.md"


def test_fetch_node_is_a_read_only_raw_get_at_the_merged_commit():
    node = _NODES["fetch_page"]["data"]

    assert node["method"] == "get"
    assert node["headers"] == "Accept: application/vnd.github.raw+json"
    assert node["url"] == (
        "{{#env.GITHUB_API_BASE#}}/repos/{{#start.repo#}}/contents/{{#page_loop.item.api_path#}}?ref={{#page_loop.item.ref#}}"
    )


def test_page_iteration_terminates_on_a_failed_child_so_no_partial_page_set_is_used():
    # Dify's ErrorHandleMode.Terminated is 'terminated' (web/app/components/workflow/types.ts at tag 1.18.0).
    assert _NODES["page_loop"]["data"]["error_handle_mode"] == "terminated"


def test_no_github_request_in_the_finder_uses_a_write_method():
    for node in _NODES.values():
        data = node["data"]
        if data.get("type") == "http-request" and "GITHUB_API_BASE" in data.get("url", ""):
            assert data["method"] == "get", node["id"]


def test_build_step_carries_the_shared_finder_helper_into_the_rendered_code():
    assert "def build_finder_inputs(" in _NODES["build_inputs"]["data"]["code"]


def test_graph_routes_files_through_the_read_path_into_prepare():
    assert _EDGES["files-read"]["target"] == "select_pages"
    assert _EDGES["pages-selected"]["target"] == "page_loop"
    assert _EDGES["pages-read"]["source"] == "page_loop"
    assert _EDGES["pages-read"]["target"] == "build_inputs"
    assert _EDGES["inputs-built"]["target"] == "prepare_context"
    sources = [edge["source"] for edge in _GRAPH["edges"] if edge["target"] == "prepare_context"]
    assert sources == ["build_inputs"]


def test_no_pages_gate_handle_ends_with_zero_findings():
    edge = _EDGES["context-no-pages"]

    assert (edge["source"], edge["sourceHandle"], edge["target"]) == ("context_gate", "no_pages", "end_no_pages")
    gate = _NODES["context_gate"]["data"]
    assert [case["case_id"] for case in gate["cases"]] == ["eligible", "no_pages"]
    assert _NODES["end_no_pages"]["data"]["outputs"] == [
        {"variable": "findings_json", "value_selector": ["prepare_context", "findings_json"]}
    ]

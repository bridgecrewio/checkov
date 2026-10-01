
def test_reduce_scan_reports_secrets(report):
    from checkov.common.bridgecrew.wrapper import reduce_scan_reports
    from checkov.common.typing import _ReducedScanReportCheck, _ReducedScanReport
    from checkov.common.bridgecrew.check_type import CheckType

    reduced_report: _ReducedScanReport = reduce_scan_reports([report])[CheckType.SECRETS]

    checks: _ReducedScanReportCheck = reduced_report["checks"]
    all_checks = checks["passed_checks"] + checks["failed_checks"] + checks["skipped_checks"]

    assert all('validation_status' in check.keys() for check in all_checks)


def test_reduce_scan_reports(report):
    from checkov.common.bridgecrew.wrapper import reduce_scan_reports
    from checkov.common.typing import _ReducedScanReportCheck, _ReducedScanReport
    from checkov.common.bridgecrew.check_type import CheckType

    report.check_type = CheckType.GITHUB_ACTIONS
    reduced_report: _ReducedScanReport = reduce_scan_reports([report])[CheckType.GITHUB_ACTIONS]

    checks: _ReducedScanReportCheck = reduced_report["checks"]
    all_checks = checks["passed_checks"] + checks["failed_checks"] + checks["skipped_checks"]

    reduced_keys = ('check_id', 'check_result', 'resource', 'file_path', 'file_line_range')

    assert all(reduced_key in check.keys() for check in all_checks for reduced_key in reduced_keys)
    assert all('validation_status' not in check.keys() for check in all_checks)


def test_persist_graphs_networkx_keeps_links_key():
    import json
    from unittest.mock import MagicMock

    from networkx import DiGraph

    from checkov.common.bridgecrew.wrapper import persist_graphs

    graph = DiGraph()
    graph.add_node("a", block_type_="resource")
    graph.add_edge("a", "b", label="depends_on")
    s3_client = MagicMock()

    persist_graphs(
        graphs={"terraform": [(graph, None)]},
        s3_client=s3_client,
        bucket="bucket",
        full_repo_object_key="repo/key",
        timeout=1,
    )

    s3_client.put_object.assert_called_once()
    body = json.loads(s3_client.put_object.call_args.kwargs["Body"])
    # the platform reads the edge list from "links" regardless of the installed networkx version
    assert "edges" not in body
    assert body["links"] == [{"source": "a", "target": "b", "label": "depends_on"}]

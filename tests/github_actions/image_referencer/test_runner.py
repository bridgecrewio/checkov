from pathlib import Path

from checkov.common.output.report import CheckType

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.github_actions.runner import Runner

from checkov.runner_filter import RunnerFilter
from pytest_mock import MockerFixture

from tests.common.image_referencer.test_utils import mock_get_license_statuses_async, mock_get_image_cached_result_async

RESOURCES_PATH = Path(__file__).parent.parent / "resources/.github/workflows"


def test_github_action_workflow(mocker: MockerFixture):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    file_name = "workflow_with_string_container.yml"
    image_name = "node:14.16"
    image_id = "sha256:2460522297"
    code_lines = "12-13"
    image_resource_postfixes = ["go", "openssl", "musl"]
    test_file = RESOURCES_PATH / file_name

    runner_filter = RunnerFilter(run_image_referencer=True)
    bc_integration.bc_source = get_source_type("disabled")

    mocker.patch(
        "checkov.common.images.image_referencer.image_scanner.get_scan_results_from_cache_async",
        side_effect=mock_get_image_cached_result_async,
    )
    mocker.patch(
        "checkov.common.images.image_referencer.get_license_statuses_async",
        side_effect=mock_get_license_statuses_async,
    )
    # 'workflow_with_string_container.yml (node:14.16 lines:12-13 (sha256:f9b91f78b0)).musl'
    reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    assert len(reports) == 2

    gha_report = next(report for report in reports if report.check_type == CheckType.GITHUB_ACTIONS)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(gha_report.resources) == 0
    assert len(gha_report.passed_checks) == 14
    assert len(gha_report.failed_checks) == 2
    assert len(gha_report.skipped_checks) == 0
    assert len(gha_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 3
    assert sca_image_report.resources == {
        f".github/workflows/{file_name} ({image_name} lines:{code_lines} ({image_id})).{postfix}"
        for postfix in image_resource_postfixes
    }
    assert sca_image_report.image_cached_results[0]["dockerImageName"] == "node:14.16"
    assert sca_image_report.image_cached_results[0]["packages"] == [
        {"type": "os", "name": "tzdata", "version": "2021a-1+deb11u5", "licenses": []}
    ]

    assert len(sca_image_report.passed_checks) == 1
    assert len(sca_image_report.failed_checks) == 4
    assert len(sca_image_report.image_cached_results) == 1
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0

from pathlib import Path

from checkov.circleci_pipelines.runner import Runner
from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.bridgecrew.check_type import CheckType

from checkov.runner_filter import RunnerFilter
from pytest_mock import MockerFixture

RESOURCES_PATH = Path(__file__).parent.parent / "resources"


def test_github_action_workflow(mocker: MockerFixture, image_cached_result, file_path):
    from checkov.common.bridgecrew.platform_integration import bc_integration
    test_file = RESOURCES_PATH / file_path

    runner_filter = RunnerFilter(run_image_referencer=True)
    bc_integration.bc_source = get_source_type("disabled")

    mocker.patch(
        "checkov.common.images.image_referencer.image_scanner.get_scan_results_from_cache",
        return_value=image_cached_result,
    )
    mocker.patch(
        "checkov.common.images.image_referencer.get_license_statuses",
        return_value=[],
    )

    reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    assert len(reports) == 2

    circleci_report = next(report for report in reports if report.check_type == CheckType.CIRCLECI_PIPELINES)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(circleci_report.resources) == 0
    assert len(circleci_report.passed_checks) == 23
    assert len(circleci_report.failed_checks) == 13
    assert len(circleci_report.skipped_checks) == 0
    assert len(circleci_report.parsing_errors) == 0

    assert len(sca_image_report.extra_resources) == 9
    assert len(sca_image_report.image_cached_results) == 9

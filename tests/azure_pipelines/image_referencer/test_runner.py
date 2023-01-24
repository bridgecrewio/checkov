from pathlib import Path

from checkov.common.output.report import CheckType

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.azure_pipelines.runner import Runner

from checkov.runner_filter import RunnerFilter
from pytest_mock import MockerFixture

from tests.common.image_referencer.test_utils import mock_get_license_statuses_async, mock_get_image_cached_result_async

RESOURCES_PATH = Path(__file__).parent / "resources/single_image"


def test_azure_pipelines_workflow(mocker: MockerFixture):
    from checkov.common.bridgecrew.platform_integration import bc_integration
    file_name = "azure-pipelines.yaml"
    image_name = "redis:latest"
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

    reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    assert len(reports) == 2

    azure_pipelines_report = next(report for report in reports if report.check_type == CheckType.AZURE_PIPELINES)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(azure_pipelines_report.resources) == 0
    assert len(azure_pipelines_report.passed_checks) == 1
    assert len(azure_pipelines_report.failed_checks) == 2
    assert len(azure_pipelines_report.skipped_checks) == 0
    assert len(azure_pipelines_report.parsing_errors) == 0


    assert sca_image_report.image_cached_results[0]["dockerImageName"] == image_name
    assert sca_image_report.image_cached_results[0]["packages"] == [
        {"type": "os", "name": "tzdata", "version": "2021a-1+deb11u5", "licenses": []}
    ]

    assert len(sca_image_report.passed_checks) == 1
    assert len(sca_image_report.failed_checks) == 4
    assert len(sca_image_report.image_cached_results) == 1
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0

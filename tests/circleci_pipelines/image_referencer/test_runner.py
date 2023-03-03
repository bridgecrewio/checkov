from pathlib import Path

from checkov.circleci_pipelines.runner import Runner
from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.bridgecrew.check_type import CheckType

from checkov.runner_filter import RunnerFilter
from pytest_mock import MockerFixture

from tests.common.image_referencer.test_utils import mock_get_empty_license_statuses_async, \
    mock_get_image_cached_result_async

RESOURCES_PATH = Path(__file__).parent.parent / "resources"


def test_circleCI_workflow(mocker: MockerFixture, file_path, image_cached_results_for_report):
    from checkov.common.bridgecrew.platform_integration import bc_integration
    test_file = RESOURCES_PATH / file_path

    runner_filter = RunnerFilter(run_image_referencer=True)
    bc_integration.bc_source = get_source_type("disabled")

    mocker.patch(
        "checkov.common.images.image_referencer.image_scanner.get_scan_results_from_cache_async",
        side_effect=mock_get_image_cached_result_async,
    )
    mocker.patch(
        "checkov.common.images.image_referencer.get_license_statuses_async",
        side_effect=mock_get_empty_license_statuses_async,
    )

    reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    assert len(reports) == 2

    circleci_report = next(report for report in reports if report.check_type == CheckType.CIRCLECI_PIPELINES)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(circleci_report.resources) == 0
    assert len(circleci_report.passed_checks) == 32
    assert len(circleci_report.failed_checks) == 13
    assert len(circleci_report.skipped_checks) == 0
    assert len(circleci_report.parsing_errors) == 0

    assert len(sca_image_report.extra_resources) == 10
    assert len(sca_image_report.image_cached_results) == 10

    got_images = ({
                'image_name': image['dockerImageName'],
                'related_resource_id': image['relatedResourceId'],
                'packages': image['packages']
                 } for image in sca_image_report.image_cached_results)
    for image in got_images:
        assert image in image_cached_results_for_report
    assert len(sca_image_report.extra_resources) == 10
    assert len(sca_image_report.image_cached_results) == 10


def test_runner_image_check(file_path):
    test_file = RESOURCES_PATH / file_path
    runner_filter = RunnerFilter(framework=['circleci_pipelines'], checks=['CKV_CIRCLECIPIPELINES_8'])

    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    assert len(report.failed_checks) == 0
    assert report.parsing_errors == []
    assert len(report.passed_checks) == 12
    assert report.skipped_checks ==[]

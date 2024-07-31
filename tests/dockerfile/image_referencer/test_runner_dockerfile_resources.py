from pathlib import Path

from pytest_mock import MockerFixture

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.bridgecrew.check_type import CheckType
from checkov.dockerfile.runner import Runner
from checkov.runner_filter import RunnerFilter
from tests.common.image_referencer.test_utils import mock_get_license_statuses_async, mock_get_image_cached_result_async

RESOURCES_PATH = Path(__file__).parent / "resources"


def test_simple_dockerfile(mocker: MockerFixture):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "Dockerfile.simple"
    image_name = "php:7.1-apache"
    code_lines = "1-1"
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

    # when
    reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    tf_report = next(report for report in reports if report.check_type == CheckType.DOCKERFILE)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 1
    assert len(tf_report.passed_checks) == 21, tf_report.get_json()
    assert len(tf_report.failed_checks) == 2
    assert len(tf_report.skipped_checks) == 0
    assert len(tf_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 3
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).musl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).openssl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).go",
    }
    assert sca_image_report.image_cached_results[0]["dockerImageName"] == "php:7.1-apache"
    assert "Dockerfile.simple.FROM" in sca_image_report.image_cached_results[0]["relatedResourceId"]
    assert sca_image_report.image_cached_results[0]["packages"] == [
        {"type": "os", "name": "tzdata", "version": "2021a-1+deb11u5", "licenses": []}
    ]

    assert len(sca_image_report.passed_checks) == 1
    assert len(sca_image_report.failed_checks) == 4
    assert len(sca_image_report.image_cached_results) == 1
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


def test_multi_stage_dockerfile(mocker: MockerFixture):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "Dockerfile.multi_stage"
    image_name_1 = "maven:3.8-openjdk-17-slim"
    image_name_2 = "amazonlinux:2"
    code_lines_1 = "2-2"
    code_lines_2 = "10-10"
    test_file = RESOURCES_PATH / file_name
    runner_filter = RunnerFilter(run_image_referencer=True)
    bc_integration.bc_source = get_source_type("disabled")

    mocker.patch(
        "checkov.common.images.image_referencer.image_scanner.get_scan_results_from_cache_async",
        side_effect=mock_get_image_cached_result_async,
    )

    # when
    reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    tf_report = next(report for report in reports if report.check_type == CheckType.DOCKERFILE)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 1
    assert len(tf_report.passed_checks) == 38, tf_report.get_json()
    assert len(tf_report.failed_checks) == 2
    assert len(tf_report.skipped_checks) == 0
    assert len(tf_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {
        f"{file_name} ({image_name_2} lines:{code_lines_2} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 3
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


def test_multi_platform_dockerfile(mocker: MockerFixture):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "Dockerfile.multi_platform"
    image_name_1 = "golang:alpine"
    image_name_2 = "alpine"
    code_lines_1 = "1-1"
    code_lines_2 = "8-8"
    test_file = RESOURCES_PATH / file_name
    runner_filter = RunnerFilter(run_image_referencer=True)
    bc_integration.bc_source = get_source_type("disabled")

    mocker.patch(
        "checkov.common.images.image_referencer.image_scanner.get_scan_results_from_cache_async",
        side_effect=mock_get_image_cached_result_async,
    )

    # when
    reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    tf_report = next(report for report in reports if report.check_type == CheckType.DOCKERFILE)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 1
    assert len(tf_report.passed_checks) == 30, tf_report.get_json()
    assert len(tf_report.failed_checks) == 3, tf_report.get_json()
    assert len(tf_report.skipped_checks) == 0, tf_report.get_json()
    assert len(tf_report.parsing_errors) == 0, tf_report.get_json()

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {
        f"{file_name} ({image_name_2} lines:{code_lines_2} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 3
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0

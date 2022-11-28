from pathlib import Path

from pytest_mock import MockerFixture

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.bridgecrew.check_type import CheckType
from checkov.dockerfile.runner import Runner
from checkov.runner_filter import RunnerFilter

RESOURCES_PATH = Path(__file__).parent / "resources"


def test_simple_dockerfile(mocker: MockerFixture, image_cached_result, license_statuses_result):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "Dockerfile.simple"
    image_name = "php:7.1-apache"
    code_lines = "1-1"
    test_file = RESOURCES_PATH / file_name
    runner_filter = RunnerFilter(run_image_referencer=True)
    bc_integration.bc_source = get_source_type("disabled")

    mocker.patch(
        "checkov.common.images.image_referencer.image_scanner.get_scan_results_from_cache",
        return_value=image_cached_result,
    )
    mocker.patch(
        "checkov.common.images.image_referencer.get_license_statuses",
        return_value=license_statuses_result,
    )

    # when
    reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    tf_report = next(report for report in reports if report.check_type == CheckType.DOCKERFILE)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 1
    assert len(tf_report.passed_checks) == 4
    assert len(tf_report.failed_checks) == 2
    assert len(tf_report.skipped_checks) == 0
    assert len(tf_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 3
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:f9b91f78b0)).musl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:f9b91f78b0)).openssl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:f9b91f78b0)).zlib",
    }
    assert sca_image_report.image_cached_results[0]["dockerImageName"] == "php:7.1-apache"
    assert "Dockerfile.simple.FROM" in sca_image_report.image_cached_results[0]["relatedResourceId"]
    assert sca_image_report.image_cached_results[0]["packages"] == [
        {"type": "os", "name": "zlib", "version": "1.2.12-r1", "licenses": ["Zlib"]}
    ]

    assert len(sca_image_report.passed_checks) == 1
    assert len(sca_image_report.failed_checks) == 2
    assert len(sca_image_report.image_cached_results) == 1
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


def test_multi_stage_dockerfile(mocker: MockerFixture, image_cached_result):
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
        "checkov.common.images.image_referencer.image_scanner.get_scan_results_from_cache",
        return_value=image_cached_result,
    )

    # when
    reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    tf_report = next(report for report in reports if report.check_type == CheckType.DOCKERFILE)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 1
    assert len(tf_report.passed_checks) == 4
    assert len(tf_report.failed_checks) == 2
    assert len(tf_report.skipped_checks) == 0
    assert len(tf_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {
        f"{file_name} ({image_name_2} lines:{code_lines_2} (sha256:f9b91f78b0)).zlib",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 1
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


def test_multi_platform_dockerfile(mocker: MockerFixture, image_cached_result):
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
        "checkov.common.images.image_referencer.image_scanner.get_scan_results_from_cache",
        return_value=image_cached_result,
    )

    # when
    reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    tf_report = next(report for report in reports if report.check_type == CheckType.DOCKERFILE)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 1
    assert len(tf_report.passed_checks) == 3
    assert len(tf_report.failed_checks) == 3
    assert len(tf_report.skipped_checks) == 0
    assert len(tf_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {
        f"{file_name} ({image_name_2} lines:{code_lines_2} (sha256:f9b91f78b0)).zlib",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 1
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0

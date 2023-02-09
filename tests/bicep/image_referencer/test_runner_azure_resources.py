from pathlib import Path

from pytest_mock import MockerFixture

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.output.report import CheckType
from checkov.runner_filter import RunnerFilter
from checkov.bicep.runner import Runner

RESOURCES_PATH = Path(__file__).parent / "resources/azure"


def test_batch_resources(mocker: MockerFixture, image_cached_result, license_statuses_result):
    # given
    from checkov.common.bridgecrew.platform_integration import bc_integration

    bc_integration.bc_source = get_source_type("disabled")

    file_name = "batch.bicep"
    image_name = "centos7"
    code_lines = "1-26"
    test_file = RESOURCES_PATH / file_name
    runner_filter = RunnerFilter(run_image_referencer=True)

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

    bicep_report = next(report for report in reports if report.check_type == CheckType.BICEP)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(bicep_report.resources) == 0
    assert len(bicep_report.passed_checks) == 0
    assert len(bicep_report.failed_checks) == 0
    assert len(bicep_report.skipped_checks) == 0
    assert len(bicep_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 3
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:f9b91f78b0)).musl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:f9b91f78b0)).openssl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:f9b91f78b0)).zlib",
    }
    assert len(sca_image_report.passed_checks) == 1
    assert len(sca_image_report.failed_checks) == 2
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0
    assert len(sca_image_report.image_cached_results) == 1

    assert sca_image_report.image_cached_results[0]["dockerImageName"] == "centos7"
    assert sca_image_report.image_cached_results[0]["relatedResourceId"].endswith(
        "bicep/image_referencer/resources/azure/batch.bicep:Microsoft.Batch/batchAccounts/pools.pool"
    )
    assert sca_image_report.image_cached_results[0]["packages"] == [
        {"type": "os", "name": "zlib", "version": "1.2.12-r1", "licenses": ["Zlib"]}
    ]


def test_container_instance_resources(mocker: MockerFixture, image_cached_result):
    # given
    file_name = "container_instance.bicep"
    image_name_1 = "busybox"
    image_name_2 = "ubuntu:20.04"
    code_lines_1 = "1-29"
    code_lines_2 = "1-29"
    test_file = RESOURCES_PATH / file_name
    runner_filter = RunnerFilter(run_image_referencer=True)

    mocker.patch(
        "checkov.common.images.image_referencer.image_scanner.get_scan_results_from_cache",
        return_value=image_cached_result,
    )
    mocker.patch(
        "checkov.common.images.image_referencer.get_license_statuses",
        return_value=[],
    )

    # when
    reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    bicep_report = next(report for report in reports if report.check_type == CheckType.BICEP)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(bicep_report.resources) == 0
    assert len(bicep_report.passed_checks) == 0
    assert len(bicep_report.failed_checks) == 0
    assert len(bicep_report.skipped_checks) == 0
    assert len(bicep_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 2
    assert sca_image_report.resources == {
        f"{file_name} ({image_name_1} lines:{code_lines_1} (sha256:f9b91f78b0)).zlib",
        f"{file_name} ({image_name_2} lines:{code_lines_2} (sha256:f9b91f78b0)).zlib",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 2
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


def test_web_resources(mocker: MockerFixture, image_cached_result):
    # given
    file_name = "web.bicep"
    image_name_1 = "nginx"
    image_name_2 = "python:3.9"
    code_lines_1 = "1-37"
    code_lines_2 = "39-75"
    test_file = RESOURCES_PATH / file_name
    runner_filter = RunnerFilter(run_image_referencer=True)

    mocker.patch(
        "checkov.common.images.image_referencer.image_scanner.get_scan_results_from_cache",
        return_value=image_cached_result,
    )
    mocker.patch(
        "checkov.common.images.image_referencer.get_license_statuses",
        return_value=[],
    )

    # when
    reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    bicep_report = next(report for report in reports if report.check_type == CheckType.BICEP)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(bicep_report.resources) == 0
    assert len(bicep_report.passed_checks) == 0
    assert len(bicep_report.failed_checks) == 0
    assert len(bicep_report.skipped_checks) == 0
    assert len(bicep_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 2
    assert sca_image_report.resources == {
        f"{file_name} ({image_name_1} lines:{code_lines_1} (sha256:f9b91f78b0)).zlib",
        f"{file_name} ({image_name_2} lines:{code_lines_2} (sha256:f9b91f78b0)).zlib",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 2
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0

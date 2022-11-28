import os
from pathlib import Path

from pytest_mock import MockerFixture

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.output.report import CheckType
from checkov.runner_filter import RunnerFilter
from checkov.cloudformation.runner import Runner

RESOURCES_PATH = Path(__file__).parent / "resources/aws"


def test_apprunner_resources(mocker: MockerFixture, image_cached_result, license_statuses_result):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "apprunner.yaml"
    image_name = "public.ecr.aws/aws-containers/hello-app-runner:latest"
    code_lines = "5-20"
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

    tf_report = next(report for report in reports if report.check_type == CheckType.CLOUDFORMATION)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 1
    assert len(tf_report.passed_checks) == 0
    assert len(tf_report.failed_checks) == 0
    assert len(tf_report.skipped_checks) == 0
    assert len(tf_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 3
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:f9b91f78b0)).musl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:f9b91f78b0)).openssl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:f9b91f78b0)).zlib",
    }
    assert (
        sca_image_report.image_cached_results[0]["dockerImageName"]
        == "public.ecr.aws/aws-containers/hello-app-runner:latest"
    )
    assert (
        "cloudformation/image_referencer/resources/aws/apprunner.yaml:AWS::AppRunner::Service.AppRunner"
        in sca_image_report.image_cached_results[0]["relatedResourceId"]
    )
    assert sca_image_report.image_cached_results[0]["packages"] == [
        {"type": "os", "name": "zlib", "version": "1.2.12-r1", "licenses": ["Zlib"]}
    ]

    assert len(sca_image_report.passed_checks) == 1
    assert len(sca_image_report.failed_checks) == 2
    assert len(sca_image_report.image_cached_results) == 1
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


def test_batch_resources(mocker: MockerFixture, image_cached_result):
    # given
    file_name = "batch.yaml"
    image_name_1 = "nvidia/cuda"
    image_name_2 = "tensorflow/tensorflow:2.10.0-gpu"
    code_lines_1 = "5-27"
    code_lines_2 = "28-44"
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

    tf_report = next(report for report in reports if report.check_type == CheckType.CLOUDFORMATION)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 2
    assert len(tf_report.passed_checks) == 0
    assert len(tf_report.failed_checks) == 0
    assert len(tf_report.skipped_checks) == 0
    assert len(tf_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 2
    assert sca_image_report.resources == {
        f"{file_name} ({image_name_1} lines:{code_lines_1} (sha256:f9b91f78b0)).zlib",
        f"{file_name} ({image_name_2} lines:{code_lines_2} (sha256:f9b91f78b0)).zlib",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 2
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


def test_codebuild_resources(mocker: MockerFixture, image_cached_result):
    # given
    file_name = "codebuild.yaml"
    image_name = "public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:3.0"
    code_lines = "5-17"
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

    tf_report = next(report for report in reports if report.check_type == CheckType.CLOUDFORMATION)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 1
    assert len(tf_report.passed_checks) == 1
    assert len(tf_report.failed_checks) == 0
    assert len(tf_report.skipped_checks) == 0
    assert len(tf_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {f"{file_name} ({image_name} lines:{code_lines} (sha256:f9b91f78b0)).zlib"}
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 1
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


def test_ecs_resources(mocker: MockerFixture, image_cached_result):
    # given
    file_name = "ecs.yaml"
    image_name_1 = "amazon/amazon-ecs-sample"
    image_name_2 = "busybox"
    code_lines_1 = "5-37"
    code_lines_2 = "5-37"
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

    tf_report = next(report for report in reports if report.check_type == CheckType.CLOUDFORMATION)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 1
    assert len(tf_report.passed_checks) == 1
    assert len(tf_report.failed_checks) == 0
    assert len(tf_report.skipped_checks) == 0
    assert len(tf_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 2
    assert sca_image_report.resources == {
        f"{file_name} ({image_name_1} lines:{code_lines_1} (sha256:f9b91f78b0)).zlib",
        f"{file_name} ({image_name_2} lines:{code_lines_2} (sha256:f9b91f78b0)).zlib",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 2
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


def test_lightsail_resources(mocker: MockerFixture, image_cached_result):
    # given
    file_name = "lightsail.yaml"
    image_name = "nginx:latest"
    code_lines = "5-13"
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

    tf_report = next(report for report in reports if report.check_type == CheckType.CLOUDFORMATION)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 1
    assert len(tf_report.passed_checks) == 0
    assert len(tf_report.failed_checks) == 0
    assert len(tf_report.skipped_checks) == 0
    assert len(tf_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {f"{file_name} ({image_name} lines:{code_lines} (sha256:f9b91f78b0)).zlib"}
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 1
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


from pathlib import Path
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.output.report import CheckType
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from tests.common.image_referencer.test_utils import (
    mock_get_empty_license_statuses_async,
    mock_get_license_statuses_async,
    mock_get_image_cached_result_async,
)
from tests.graph_utils.utils import GRAPH_FRAMEWORKS

RESOURCES_PATH = Path(__file__).parent / "resources/gcp"


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_cloud_run_resources(mocker: MockerFixture, graph_framework):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "cloud_run.tf"
    image_name = "gcr.io/cloudrun/hello"
    code_lines = "1-17"
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
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    tf_report = next(report for report in reports if report.check_type == CheckType.TERRAFORM)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 1
    assert len(tf_report.passed_checks) == 0
    assert len(tf_report.failed_checks) == 0
    assert len(tf_report.skipped_checks) == 0
    assert len(tf_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 3
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).musl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).openssl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).go",
    }
    assert sca_image_report.image_cached_results[0]["dockerImageName"] == "gcr.io/cloudrun/hello"
    assert (
            "terraform/image_referencer/resources/gcp/cloud_run.tf:google_cloud_run_service.example"
            in sca_image_report.image_cached_results[0]["relatedResourceId"]
    )
    assert sca_image_report.image_cached_results[0]["packages"] == [
        {"type": "os", "name": "tzdata", "version": "2021a-1+deb11u5", "licenses": []}
    ]

    assert len(sca_image_report.passed_checks) == 1
    assert len(sca_image_report.failed_checks) == 4
    assert len(sca_image_report.image_cached_results) == 1
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_cloud_run_v2_resources(mocker: MockerFixture, graph_framework):
    # given
    file_name = "cloud_run_v2.tf"
    image_name_1 = "gcr.io/cloudrun/job"
    image_name_2 = "gcr.io/cloudrun/hello"
    code_lines_1 = "1-13"
    code_lines_2 = "15-29"
    test_file = RESOURCES_PATH / file_name
    runner_filter = RunnerFilter(run_image_referencer=True)

    mocker.patch(
        "checkov.common.images.image_referencer.image_scanner.get_scan_results_from_cache_async",
        side_effect=mock_get_image_cached_result_async,
    )
    mocker.patch(
        "checkov.common.images.image_referencer.get_license_statuses_async",
        side_effect=mock_get_empty_license_statuses_async,
    )

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    tf_report = next(report for report in reports if report.check_type == CheckType.TERRAFORM)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 2
    assert len(tf_report.passed_checks) == 0
    assert len(tf_report.failed_checks) == 0
    assert len(tf_report.skipped_checks) == 0
    assert len(tf_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 2
    assert sca_image_report.resources == {
        f"{file_name} ({image_name_1} lines:{code_lines_1} (sha256:2460522297)).go",
        f"{file_name} ({image_name_2} lines:{code_lines_2} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 6
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_cloudbuild_resources(mocker: MockerFixture, graph_framework):
    # given
    file_name = "cloudbuild.tf"
    image_name_1 = "gcr.io/cloud-builders/gsutil"
    image_name_2 = "ubuntu"
    code_lines_1 = "1-72"
    code_lines_2 = "1-72"
    test_file = RESOURCES_PATH / file_name
    runner_filter = RunnerFilter(run_image_referencer=True)

    mocker.patch(
        "checkov.common.images.image_referencer.image_scanner.get_scan_results_from_cache_async",
        side_effect=mock_get_image_cached_result_async,
    )
    mocker.patch(
        "checkov.common.images.image_referencer.get_license_statuses_async",
        side_effect=mock_get_empty_license_statuses_async,
    )

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    tf_report = next(report for report in reports if report.check_type == CheckType.TERRAFORM)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(tf_report.resources) == 1
    assert len(tf_report.passed_checks) == 0
    assert len(tf_report.failed_checks) == 0
    assert len(tf_report.skipped_checks) == 0
    assert len(tf_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 2
    assert sca_image_report.resources == {
        f"{file_name} ({image_name_1} lines:{code_lines_1} (sha256:2460522297)).go",
        f"{file_name} ({image_name_2} lines:{code_lines_2} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 6
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0

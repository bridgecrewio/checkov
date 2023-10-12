from pathlib import Path
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.output.report import CheckType
from checkov.runner_filter import RunnerFilter
from checkov.bicep.runner import Runner
from tests.common.image_referencer.test_utils import (
    mock_get_empty_license_statuses_async,
    mock_get_license_statuses_async,
    mock_get_image_cached_result_async,
)
from tests.graph_utils.utils import GRAPH_FRAMEWORKS

RESOURCES_PATH = Path(__file__).parent / "resources/azure"


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_batch_resources(mocker: MockerFixture, graph_framework):
    # given
    from checkov.common.bridgecrew.platform_integration import bc_integration

    bc_integration.bc_source = get_source_type("disabled")

    file_name = "batch.bicep"
    image_name = "centos7"
    code_lines = "1-27"
    test_file = RESOURCES_PATH / file_name
    runner_filter = RunnerFilter(run_image_referencer=True)

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

    bicep_report = next(report for report in reports if report.check_type == CheckType.BICEP)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(bicep_report.resources) == 0
    assert len(bicep_report.passed_checks) == 0
    assert len(bicep_report.failed_checks) == 0
    assert len(bicep_report.skipped_checks) == 0
    assert len(bicep_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 3
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).musl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).openssl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 1
    assert len(sca_image_report.failed_checks) == 4
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0
    assert len(sca_image_report.image_cached_results) == 1

    assert sca_image_report.image_cached_results[0]["dockerImageName"] == "centos7"
    assert sca_image_report.image_cached_results[0]["relatedResourceId"].endswith(
        "bicep/image_referencer/resources/azure/batch.bicep:Microsoft.Batch/batchAccounts/pools.pool"
    )
    assert sca_image_report.image_cached_results[0]["packages"] == [
        {"type": "os", "name": "tzdata", "version": "2021a-1+deb11u5", "licenses": []}
    ]


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_container_instance_resources(mocker: MockerFixture, graph_framework):
    # given
    file_name = "container_instance.bicep"
    image_name_1 = "busybox"
    image_name_2 = "ubuntu:20.04"
    code_lines_1 = "1-29"
    code_lines_2 = "1-29"
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

    bicep_report = next(report for report in reports if report.check_type == CheckType.BICEP)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(bicep_report.resources) == 0
    assert len(bicep_report.passed_checks) == 0
    assert len(bicep_report.failed_checks) == 0
    assert len(bicep_report.skipped_checks) == 0
    assert len(bicep_report.parsing_errors) == 0

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
def test_web_resources(mocker: MockerFixture, graph_framework):
    # given
    file_name = "web.bicep"
    image_name_1 = "nginx"
    image_name_2 = "python:3.9"
    code_lines_1 = "1-37"
    code_lines_2 = "39-75"
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

    bicep_report = next(report for report in reports if report.check_type == CheckType.BICEP)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(bicep_report.resources) == 0
    assert len(bicep_report.passed_checks) == 0
    assert len(bicep_report.failed_checks) == 0
    assert len(bicep_report.skipped_checks) == 0
    assert len(bicep_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 2
    assert sca_image_report.resources == {
        f"{file_name} ({image_name_1} lines:{code_lines_1} (sha256:2460522297)).go",
        f"{file_name} ({image_name_2} lines:{code_lines_2} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 6
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0

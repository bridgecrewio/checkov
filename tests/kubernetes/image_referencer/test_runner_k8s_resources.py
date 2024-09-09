from pathlib import Path
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.output.report import CheckType
from checkov.runner_filter import RunnerFilter
from checkov.kubernetes.runner import Runner
from tests.common.image_referencer.test_utils import (
    mock_get_empty_license_statuses_async,
    mock_get_license_statuses_async,
    mock_get_image_cached_result_async,
)
from tests.graph_utils.utils import GRAPH_FRAMEWORKS

RESOURCES_PATH = Path(__file__).parent / "resources/k8s"


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_pod_resources(mocker: MockerFixture, graph_framework):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "pod.yaml"
    image_name = "nginx:latest"
    code_lines = "1-14"
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

    k8s_report = next(report for report in reports if report.check_type == CheckType.KUBERNETES)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(k8s_report.resources) == 1
    assert len(k8s_report.passed_checks) == 69
    assert len(k8s_report.failed_checks) == 20
    assert len(k8s_report.skipped_checks) == 0
    assert len(k8s_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 3
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).musl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).openssl",
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).go",
    }
    assert sca_image_report.image_cached_results[0]["dockerImageName"] == "nginx:latest"
    assert (
        "kubernetes/image_referencer/resources/k8s/pod.yaml:Pod.default.webserver"
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
def test_cron_job_resources(mocker: MockerFixture, graph_framework):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "cron_job.yaml"
    image_name = "busybox:1.28"
    code_lines = "1-20"
    test_file = RESOURCES_PATH / file_name
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

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    k8s_report = next(report for report in reports if report.check_type == CheckType.KUBERNETES)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(k8s_report.resources) == 1
    assert len(k8s_report.passed_checks) == 69
    assert len(k8s_report.failed_checks) == 17
    assert len(k8s_report.skipped_checks) == 0
    assert len(k8s_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 3
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_daemon_set_resources(mocker: MockerFixture, graph_framework):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "daemon_set.yaml"
    image_name = "newrelic/infrastructure"
    code_lines = "11-59"
    test_file = RESOURCES_PATH / file_name
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

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    k8s_report = next(report for report in reports if report.check_type == CheckType.KUBERNETES)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(k8s_report.resources) == 2
    assert len(k8s_report.passed_checks) == 66
    assert len(k8s_report.failed_checks) == 23
    assert len(k8s_report.skipped_checks) == 0
    assert len(k8s_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 3
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_deployment_resources(mocker: MockerFixture, graph_framework):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "deployment.yaml"
    image_name = "minio/minio:latest"
    code_lines = "13-44"
    test_file = RESOURCES_PATH / file_name
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

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    k8s_report = next(report for report in reports if report.check_type == CheckType.KUBERNETES)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(k8s_report.resources) == 2
    assert len(k8s_report.passed_checks) == 68
    assert len(k8s_report.failed_checks) == 21
    assert len(k8s_report.skipped_checks) == 0
    assert len(k8s_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 3
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_deployment_config_resources(mocker: MockerFixture, graph_framework):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "deployment_config.yaml"
    image_name = "rhel7/rhel-tools"
    code_lines = "10-26"
    test_file = RESOURCES_PATH / file_name
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

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    k8s_report = next(report for report in reports if report.check_type == CheckType.KUBERNETES)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(k8s_report.resources) == 2
    assert len(k8s_report.passed_checks) == 65
    assert len(k8s_report.failed_checks) == 14
    assert len(k8s_report.skipped_checks) == 0
    assert len(k8s_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 3
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_job_resources(mocker: MockerFixture, graph_framework):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "job.yaml"
    image_name = "perl:5.34.0"
    code_lines = "1-14"
    test_file = RESOURCES_PATH / file_name
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

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    k8s_report = next(report for report in reports if report.check_type == CheckType.KUBERNETES)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(k8s_report.resources) == 1
    assert len(k8s_report.passed_checks) == 69
    assert len(k8s_report.failed_checks) == 17
    assert len(k8s_report.skipped_checks) == 0
    assert len(k8s_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 3
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_pod_template_resources(mocker: MockerFixture, graph_framework):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "pod_template.yaml"
    image_name = "alpine"
    code_lines = "1-14"
    test_file = RESOURCES_PATH / file_name
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

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    k8s_report = next(report for report in reports if report.check_type == CheckType.KUBERNETES)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(k8s_report.resources) == 1
    assert len(k8s_report.passed_checks) == 65
    assert len(k8s_report.failed_checks) == 13
    assert len(k8s_report.skipped_checks) == 0
    assert len(k8s_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 3
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_replica_set_resources(mocker: MockerFixture, graph_framework):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "replica_set.yaml"
    image_name = "gcr.io/google_samples/gb-frontend:v3"
    code_lines = "15-22"
    test_file = RESOURCES_PATH / file_name
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

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    k8s_report = next(report for report in reports if report.check_type == CheckType.KUBERNETES)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(k8s_report.resources) == 2
    assert len(k8s_report.passed_checks) == 69
    assert len(k8s_report.failed_checks) == 20
    assert len(k8s_report.skipped_checks) == 0
    assert len(k8s_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 3
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


@pytest.mark.parametrize("graph_framework", GRAPH_FRAMEWORKS)
def test_replication_controller_resources(mocker: MockerFixture, graph_framework):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "replication_controller.yaml"
    image_name_1 = "busybox"
    image_name_2 = "quay.io/pires/docker-elasticsearch-kubernetes:5.6.2"
    code_lines_1 = "10-59"
    code_lines_2 = "10-59"
    test_file = RESOURCES_PATH / file_name
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

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    k8s_report = next(report for report in reports if report.check_type == CheckType.KUBERNETES)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(k8s_report.resources) == 2
    assert len(k8s_report.passed_checks) == 67
    assert len(k8s_report.failed_checks) == 22
    assert len(k8s_report.skipped_checks) == 0
    assert len(k8s_report.parsing_errors) == 0

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
def test_stateful_set_resources(mocker: MockerFixture, graph_framework):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "stateful_set.yaml"
    image_name_1 = "cockroachdb/cockroach-k8s-init:0.2"
    image_name_2 = "cockroachdb/cockroach:v1.1.0"
    code_lines_1 = "14-100"
    code_lines_2 = "14-100"
    test_file = RESOURCES_PATH / file_name
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

    # when
    with mock.patch.dict('os.environ', {'CHECKOV_GRAPH_FRAMEWORK': graph_framework}):
        reports = Runner().run(root_folder="", files=[str(test_file)], runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    k8s_report = next(report for report in reports if report.check_type == CheckType.KUBERNETES)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(k8s_report.resources) == 2
    assert len(k8s_report.passed_checks) == 69
    assert len(k8s_report.failed_checks) == 20
    assert len(k8s_report.skipped_checks) == 0
    assert len(k8s_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 2
    assert sca_image_report.resources == {
        f"{file_name} ({image_name_1} lines:{code_lines_1} (sha256:2460522297)).go",
        f"{file_name} ({image_name_2} lines:{code_lines_2} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 6
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0


from __future__ import annotations

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.bridgecrew.check_type import CheckType
from checkov.helm.runner import Runner
from checkov.runner_filter import RunnerFilter
from tests.common.image_referencer.test_utils import (
    mock_get_empty_license_statuses_async,
    mock_get_image_cached_result_async,
)
from tests.helm.utils import helm_exists

RESOURCES_PATH = Path(__file__).parent / "runner/resources"


@pytest.mark.skipif(not helm_exists(), reason="helm not installed")
def test_deployment_resources(mocker: MockerFixture):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    file_name = "hello-world/templates/deployment.yaml"
    image_name = "nginx:1.16.0"
    code_lines = "20-42"
    test_folder = RESOURCES_PATH / "image_referencer"
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
    reports = Runner().run(root_folder=str(test_folder), runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    helm_report = next(report for report in reports if report.check_type == CheckType.HELM)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(helm_report.resources) == 4
    assert len(helm_report.passed_checks) == 72
    assert len(helm_report.failed_checks) == 20
    assert len(helm_report.skipped_checks) == 0
    assert len(helm_report.parsing_errors) == 0

    assert len(sca_image_report.resources) == 1
    assert sca_image_report.resources == {
        f"{file_name} ({image_name} lines:{code_lines} (sha256:2460522297)).go",
    }
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 3
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0
    assert len(sca_image_report.image_cached_results) == 1

    assert sca_image_report.image_cached_results[0]["dockerImageName"] == image_name
    assert (
        sca_image_report.image_cached_results[0]["relatedResourceId"]
        == "/hello-world/templates/deployment.yaml:Pod.default.release-name-hello-world.app.kubernetes.io/name-hello-world.app.kubernetes.io/instance-release-name"
    )
    assert sca_image_report.image_cached_results[0]["packages"] == [
        {"type": "os", "name": "tzdata", "version": "2021a-1+deb11u5", "licenses": []}
    ]

from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.bridgecrew.check_type import CheckType
from checkov.kustomize.runner import Runner
from checkov.runner_filter import RunnerFilter
from tests.common.image_referencer.test_utils import (
    mock_get_empty_license_statuses_async,
    mock_get_image_cached_result_async,
)
from tests.kustomize.utils import kustomize_exists

RESOURCES_PATH = Path(__file__).parent / "runner/resources"


@pytest.mark.xfail(reason="This is probably connected to the OS + kustomize version")
@pytest.mark.skipif(os.name == "nt" or not kustomize_exists(), reason="kustomize not installed or Windows OS")
@pytest.mark.parametrize("allow_kustomize_file_edits, code_lines", [
    (True, "18-34"),
    (False, "15-31")
])
def test_deployment_resources(mocker: MockerFixture, allow_kustomize_file_edits: bool, code_lines: str):
    from checkov.common.bridgecrew.platform_integration import bc_integration

    # given
    image_name = "wordpress:4.8-apache"
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

    with mock.patch.dict(os.environ, {"CHECKOV_ALLOW_KUSTOMIZE_FILE_EDITS": str(allow_kustomize_file_edits)}):
        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        runner.templateRendererCommandOptions = "build"
        reports = runner.run(root_folder=str(test_folder), runner_filter=runner_filter)

    # then
    assert len(reports) == 2

    kustomize_report = next(report for report in reports if report.check_type == CheckType.KUSTOMIZE)
    sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(kustomize_report.resources) == 6
    assert len(kustomize_report.passed_checks) == 136
    assert len(kustomize_report.failed_checks) == 42
    assert len(kustomize_report.skipped_checks) == 0
    assert len(kustomize_report.parsing_errors) == 0

    if allow_kustomize_file_edits:
        for record in kustomize_report.failed_checks:
            assert record.caller_file_path in ['/base/deployment.yaml', '/base/service.yaml', '/deployment.yaml',
                                               '/service.yaml']

    assert len(sca_image_report.resources) == 2
    assert f'base/kustomization.yaml (wordpress:4.8-apache lines:{code_lines} (sha256:2460522297)).go' in \
           sca_image_report.resources
    assert f'overlays/prod/kustomization.yaml (wordpress:4.8-apache lines:{code_lines} (sha256:2460522297)).go' in \
           sca_image_report.resources
    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 6
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0
    assert len(sca_image_report.image_cached_results) == 2

    assert sca_image_report.image_cached_results[0]["dockerImageName"] == image_name
    assert (
        sca_image_report.image_cached_results[0]["relatedResourceId"].endswith("/kustomization.yaml:Pod.default.prod-wordpress.app-wordpress")
    )
    assert sca_image_report.image_cached_results[0]["packages"] == [
        {"type": "os", "name": "tzdata", "version": "2021a-1+deb11u5", "licenses": []}
    ]

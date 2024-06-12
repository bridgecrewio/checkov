from __future__ import annotations

from typing import Any

import pytest
from unittest import mock
import responses
from pathlib import Path

from checkov.common.bridgecrew.bc_source import SourceType
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration, bc_integration
from checkov.runner_filter import RunnerFilter
from checkov.sca_image.runner import Runner
from checkov.common.output.report import Report
from .mocks import mock_scan

KUBERNETES_EXAMPLES_DIR = Path(__file__).parent / "examples/kubernetes"
DOCKERFILE_EXAMPLES_DIR = Path(__file__).parent / "examples/dockerfile"

@pytest.fixture()
def image_id() -> str:
    return "sha256:6fd085fc6410"


@pytest.fixture(scope='package')
def mock_bc_integration() -> BcPlatformIntegration:
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    bc_integration.setup_bridgecrew_credentials(
        repo_id="bridgecrewio/checkov",
        skip_fixes=True,
        skip_download=True,
        source=SourceType("Github", False),
        source_version="1.0",
        repo_branch="master",
    )
    return bc_integration


@pytest.fixture()
def empty_report() -> dict[str, Any]:
    return {
        "check_type": "sca_image",
        "failing_checks": [],
        "passed_checks": [],
        "parsing_errors": [],
        "resources": {},
        "skipped_checks": [],
    }


@pytest.fixture()
def image_name() -> str:
    return "ubuntu"


@pytest.fixture()
def cached_scan_result() -> dict[str, str]:
    return {
        "outputType": "Result",
        "outputData": (
            "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"
            "2d/P767/8DpWNycPggAAA="
        ),
        "compressionMethod": "gzip",
    }


@pytest.fixture()
def image_name2() -> str:
    return "node:14.16"


@pytest.fixture()
def cached_scan_result2() -> dict[str, str]:
    return {'outputType': 'Result', 'outputData': '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', 'compressionMethod': 'gzip'}


@pytest.fixture()
def cached_scan_result3() -> dict[str, str]:
    return {'outputType': 'Error', 'outputData': '', 'compressionMethod': 'gzip'}


@mock.patch('checkov.sca_image.runner.Runner.scan', mock_scan)
@responses.activate
def get_sca_image_report(mock_bc_integration: BcPlatformIntegration) -> Report:
    response_json = {
        "violations": [
            {
                "name": "pcre2",
                "version": "10.39-3build1",
                "license": "Apache-2.0",
                "policy": "BC_LIC_1",
                "status": "COMPLIANT"
            },
            {
                "name": "perl",
                "version": "5.34.0-3ubuntu1",
                "license": "Apache-2.0-Fake",
                "policy": "BC_LIC_1",
                "status": "OPEN"
            },
        ]
    }
    responses.add(
        method=responses.POST,
        url=mock_bc_integration.api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
        json=response_json,
        status=200
    )

    runner = Runner()
    runner_filter = RunnerFilter(skip_checks=["CKV_CVE_2022_1586"])
    dockerfile_path = "/path/to/Dockerfile"
    image_id = "sha256:123456"
    return runner.run(root_folder=DOCKERFILE_EXAMPLES_DIR, runner_filter=runner_filter,
                      dockerfile_path=dockerfile_path, image_id=image_id)


@pytest.fixture(scope='package')
def sca_image_report(mock_bc_integration: BcPlatformIntegration) -> Report:
    return get_sca_image_report(mock_bc_integration)


@pytest.fixture(scope='function')
def sca_image_report_scope_function(mock_bc_integration: BcPlatformIntegration) -> Report:
    return get_sca_image_report(mock_bc_integration)

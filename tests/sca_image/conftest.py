from typing import Dict, Any

import pytest

from checkov.common.bridgecrew.bc_source import SourceType
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration, bc_integration


@pytest.fixture()
def image_id() -> str:
    return "sha256:6fd085fc6410"


@pytest.fixture()
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
def empty_report() -> Dict[str, Any]:
    return {
        'check_type': 'sca_image',
        'failing_checks': [],
        'passed_checks': [],
        'parsing_errors': [],
        'resources': {},
        'skipped_checks': []
    }

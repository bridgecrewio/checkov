
from copy import deepcopy
import os
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.util.http_utils import normalize_bc_url, normalize_prisma_url
import pytest

@pytest.fixture(scope='module', autouse=True)
def clean_bc_integration() -> None:
    from checkov.common.bridgecrew.platform_integration import bc_integration
    bc_integration.bc_api_key = None
    bc_integration.s3_client = None
    bc_integration.bucket: str | None = None
    bc_integration.credentials: dict[str, str] | None = None
    bc_integration.repo_path: str | None = None
    bc_integration.support_bucket: str | None = None
    bc_integration.support_repo_path: str | None = None
    bc_integration.repo_id: str | None = None
    bc_integration.repo_branch: str | None = None
    bc_integration.skip_fixes = False  # even though we removed the CLI flag, this gets set so we know whether this is a fix run (IDE) or not (normal CLI)
    bc_integration.skip_download = False
    bc_integration.source_id: str | None = None
    bc_integration.bc_source = None
    bc_integration.bc_source_version: str | None = None
    bc_integration.timestamp: str | None = None
    bc_integration.scan_reports = []
    bc_integration.bc_api_url = normalize_bc_url(os.getenv('BC_API_URL', "https://www.bridgecrew.cloud"))
    bc_integration.prisma_api_url = normalize_prisma_url(os.getenv("PRISMA_API_URL"))
    bc_integration.prisma_policies_url: str | None = None
    bc_integration.prisma_policy_filters_url: str | None = None
    bc_integration.setup_api_urls()
    bc_integration.customer_run_config_response = None
    bc_integration.prisma_policies_response = None
    bc_integration.public_metadata_response = None
    bc_integration.use_s3_integration = False
    bc_integration.s3_setup_failed = False
    bc_integration.platform_integration_configured = False
    bc_integration.http= None
    bc_integration.bc_skip_mapping = False
    bc_integration.cicd_details = {}
    bc_integration.support_flag_enabled = False
    bc_integration.enable_persist_graphs = True
    bc_integration.persist_graphs_timeout = int(os.getenv('BC_PERSIST_GRAPHS_TIMEOUT', 60))
    bc_integration.ca_certificate: str | None = None
    bc_integration.no_cert_verify: bool = False
    bc_integration.on_prem: bool = False
    bc_integration.daemon_process = False  # set to 'True' when running in multiprocessing 'spawn' mode
    bc_integration.scan_dir = []
    bc_integration.scan_file = []

@pytest.fixture(scope='module', autouse=True)
def clean_feature_registry():
    from checkov.common.bridgecrew.integration_features.integration_feature_registry import integration_feature_registry
    old_features = deepcopy(integration_feature_registry.features)
    before_registred_checks = deepcopy(BaseCheckRegistry._BaseCheckRegistry__all_registered_checks)
    yield
    integration_feature_registry.features = deepcopy(old_features)
    BaseCheckRegistry._BaseCheckRegistry__all_registered_checks = before_registred_checks




@pytest.fixture(scope='module', autouse=True)
def reset_checks():
    from checkov.terraform.checks.resource.registry import resource_registry as registry
    before_checks = deepcopy(registry.checks)
    before_wildcards_checks = deepcopy(registry.wildcard_checks)
    yield
    registry.checks = before_checks
    registry.wildcard_checks = before_wildcards_checks
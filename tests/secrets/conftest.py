import pytest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.models.enums import CheckResult

from checkov.common.bridgecrew.bc_source import SourceType

from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration, bc_integration
from checkov.common.output.report import Report
from checkov.common.output.secrets_record import SecretsRecord


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


@pytest.fixture(scope='function')
def mock_bc_integration_no_api_key() -> BcPlatformIntegration:
    bc_integration.bc_api_key = None
    return bc_integration


@pytest.fixture
def secrets_report() -> Report:
    kwargs = {'validation_status': 'mock', 'check_id': 'mock', 'check_name': 'mock', 'code_block': 'mock', 'file_path': 'mock',
              'file_line_range': 'mock', 'evaluations': 'mock', 'check_class': 'mock', 'file_abs_path': 'mock'}
    record_1 = SecretsRecord(bc_check_id="VIOLATION_1", resource="RESOURCE_1", check_result={"result": CheckResult.FAILED}, **kwargs)
    record_2 = SecretsRecord(bc_check_id="VIOLATION_2", resource="RESOURCE_2", check_result={"result": CheckResult.FAILED}, **kwargs)
    record_3 = SecretsRecord(bc_check_id="VIOLATION_3", resource="RESOURCE_3", check_result={"result": CheckResult.FAILED}, **kwargs)
    record_4 = SecretsRecord(bc_check_id="VIOLATION_4", resource="RESOURCE_4", check_result={"result": CheckResult.FAILED}, **kwargs)

    record_5 = SecretsRecord(bc_check_id="VIOLATION_1", resource="RESOURCE_1", check_result={"result": CheckResult.PASSED}, **kwargs)

    report = Report(CheckType.SECRETS)
    report.add_record(record_1)
    report.add_record(record_2)
    report.add_record(record_3)
    report.add_record(record_4)
    report.add_record(record_5)

    return report

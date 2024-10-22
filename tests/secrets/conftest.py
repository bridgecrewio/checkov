import pytest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.models.enums import CheckResult
from checkov.common.output.report import Report
from checkov.common.output.secrets_record import SecretsRecord


@pytest.fixture
def mock_bc_integration():
    from checkov.common.bridgecrew.platform_integration import bc_integration
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    bc_integration.skip_download = False
    return bc_integration


@pytest.fixture
def mock_metadata_integration():
    from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration

    check_metadata = integration.check_metadata
    integration.check_metadata = {
        "CKV_SECRET_2": {
            "id": "BC_GIT_2",
            "checkovId": "CKV_SECRET_2",
        },
        "CKV_SECRET_6": {
            "id": "BC_GIT_6",
            "checkovId": "CKV_SECRET_6",
        }
    }

    yield

    integration.check_metadata = check_metadata


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


@pytest.fixture
def secrets_report_invalid_status() -> Report:
    kwargs = {'check_id': 'mock', 'check_name': 'mock', 'code_block': 'mock',
              'file_path': 'mock',
              'file_line_range': 'mock', 'evaluations': 'mock', 'check_class': 'mock', 'file_abs_path': 'mock'}
    record_1 = SecretsRecord(bc_check_id="VIOLATION_1", resource="RESOURCE_1",
                             check_result={"result": CheckResult.FAILED}, validation_status='Invalid', **kwargs)
    record_2 = SecretsRecord(bc_check_id="VIOLATION_2", resource="RESOURCE_2",
                             check_result={"result": CheckResult.FAILED}, validation_status='Invalid', **kwargs)
    record_3 = SecretsRecord(bc_check_id="VIOLATION_3", resource="RESOURCE_3",
                             check_result={"result": CheckResult.FAILED}, validation_status='Invalid', **kwargs)
    record_4 = SecretsRecord(bc_check_id="VIOLATION_4", resource="RESOURCE_4",
                             check_result={"result": CheckResult.FAILED}, validation_status='Invalid', **kwargs)

    record_5 = SecretsRecord(bc_check_id="VIOLATION_1", resource="RESOURCE_1",
                             check_result={"result": CheckResult.PASSED}, validation_status='Invalid', **kwargs)

    report = Report(CheckType.SECRETS)
    report.add_record(record_1)
    report.add_record(record_2)
    report.add_record(record_3)
    report.add_record(record_4)
    report.add_record(record_5)

    return report

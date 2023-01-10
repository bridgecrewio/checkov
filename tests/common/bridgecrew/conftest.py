import pytest
from checkov.common.models.enums import CheckResult

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.secrets_record import SecretsRecord

from checkov.common.output.report import Report

kwargs = {'validation_status': 'mock', 'check_id': 'mock', 'check_name': 'mock', 'code_block': 'mock',
          'file_path': 'mock',
          'file_line_range': 'mock', 'evaluations': 'mock', 'check_class': 'mock', 'file_abs_path': 'mock'}


@pytest.fixture
def report() -> Report:
    record_1 = SecretsRecord(bc_check_id="VIOLATION_1", resource="RESOURCE_1",
                             check_result={"result": CheckResult.FAILED}, **kwargs)
    record_2 = SecretsRecord(bc_check_id="VIOLATION_2", resource="RESOURCE_2",
                             check_result={"result": CheckResult.FAILED}, **kwargs)

    record_3 = SecretsRecord(bc_check_id="VIOLATION_3", resource="RESOURCE_1",
                             check_result={"result": CheckResult.PASSED}, **kwargs)

    record_4 = SecretsRecord(bc_check_id="VIOLATION_1", resource="RESOURCE_2",
                             check_result={"result": CheckResult.SKIPPED}, **kwargs)

    report = Report(CheckType.SECRETS)
    report.add_record(record_1)
    report.add_record(record_2)
    report.add_record(record_3)
    report.add_record(record_4)

    return report

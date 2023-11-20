import pytest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.models.enums import CheckResult
from checkov.sast.checks_infra.base_registry import Registry
from checkov.sast.engines.prisma_engine import PrismaEngine
from checkov.sast.runner import Runner
from checkov.runner_filter import RunnerFilter
import pathlib
import os


@pytest.mark.skip(reason="should move test to an integration test once sast supports skipping default policies")
def test_sast_runner_python():
    runner = Runner()
    cur_dir = pathlib.Path(__file__).parent.resolve()
    source = os.path.join(cur_dir, 'source_code')
    external_dir_checks = os.path.join(cur_dir, 'external_checks')
    reports = runner.run(source, runner_filter=RunnerFilter(framework=['sast_python']),
                         external_checks_dir=[str(external_dir_checks)])

    assert len(reports) == 1
    assert reports[0].check_type == CheckType.SAST_PYTHON
    python_report = reports[0]
    assert len(python_report.failed_checks) > 0
    python_record = next((record for record in python_report.failed_checks if record.check_id == 'CKV3_SAST_11'), None)
    assert python_record
    assert python_record.severity.name == 'MEDIUM'
    assert python_record.file_path == 'fail.py'
    assert python_record.check_name == 'Ensure superuser port is not set'
    assert python_record.code_block == [(2, 'set_port(443)\n')]
    assert python_record.file_abs_path == os.path.join(source, 'external_check', 'fail.py')
    assert python_record.file_line_range == [2, 2]
    assert python_record.check_result.get('result') == CheckResult.FAILED


@pytest.mark.skip(reason="should move test to an integration test once sast supports skipping default policies")
def test_sast_runner():
    runner = Runner()
    cur_dir = pathlib.Path(__file__).parent.resolve()
    source = os.path.join(cur_dir / 'source_code' / 'external_check')
    external_dir_checks = os.path.join(cur_dir, 'external_checks')
    reports = runner.run(source,
                         runner_filter=RunnerFilter(framework=['sast'], checks=['CKV3_SAST_11', 'seam-log-injection']),
                         external_checks_dir=[external_dir_checks], )
    assert len(reports) == 2
    python_report = next(report for report in reports if report.check_type == CheckType.SAST_PYTHON)
    assert len(python_report.failed_checks) == 1
    assert python_report.failed_checks[0].check_id == 'CKV3_SAST_11'
    assert python_report.failed_checks[0].severity.name == 'MEDIUM'
    assert python_report.failed_checks[0].file_path == 'fail.py'
    assert python_report.failed_checks[0].check_name == 'Ensure superuser port is not set'
    assert python_report.failed_checks[0].code_block == [(2, 'set_port(443)\n')]
    assert python_report.failed_checks[0].file_abs_path == os.path.join(source, 'fail.py')
    assert python_report.failed_checks[0].file_line_range == [2, 2]
    assert python_report.failed_checks[0].check_result.get('result') == CheckResult.FAILED

    java_report = next(report for report in reports if report.check_type == CheckType.SAST_JAVA)
    assert len(java_report.failed_checks) == 2
    assert java_report.failed_checks[0].check_id == 'seam-log-injection'
    assert java_report.failed_checks[0].severity.name == 'HIGH'
    assert java_report.failed_checks[0].file_path == 'fail.java'
    assert java_report.failed_checks[0].check_name == 'seam log injection'
    assert java_report.failed_checks[0].code_block == [
        (31, 'log.info("request: method="+httpRequest.getMethod()+", URL="+httpRequest.getRequestURI());\n')]
    assert java_report.failed_checks[0].file_abs_path == os.path.join(source, 'fail.java')
    assert java_report.failed_checks[0].file_line_range == [31, 31]
    assert java_report.failed_checks[0].check_result.get('result') == CheckResult.FAILED

    assert java_report.failed_checks[1].check_id == 'seam-log-injection'
    assert java_report.failed_checks[1].severity.name == 'HIGH'
    assert java_report.failed_checks[1].file_path == 'fail.java'
    assert java_report.failed_checks[1].check_name == 'seam log injection'
    assert java_report.failed_checks[1].code_block == [
        (40, 'log.info("Current logged in user : " + user.getUsername());\n')]
    assert java_report.failed_checks[1].file_abs_path == os.path.join(source, 'fail.java')
    assert java_report.failed_checks[1].file_line_range == [40, 40]
    assert java_report.failed_checks[1].check_result.get('result') == CheckResult.FAILED


@pytest.mark.skip(reason="This test should be an integration test")
def test_sast_prisma_runner(mocker):
    temp = bc_integration.bc_api_key
    bc_integration.bc_api_key = "123456"

    mocker.patch("checkov.sast.engines.prisma_engine.PrismaEngine.run_go_library", return_value=[])
    mocker.patch("checkov.sast.engines.prisma_engine.PrismaEngine.setup_sast_artifact", return_value='')
    mocker.patch("checkov.sast.engines.prisma_engine.PrismaEngine.get_sast_artifact", return_value='')

    runner = Runner()
    cur_dir = pathlib.Path(__file__).parent.resolve()
    source = os.path.join(cur_dir / 'source_code' / 'external_check')
    external_dir_checks = os.path.join(cur_dir, 'external_checks')
    reports = runner.run(source,
                         runner_filter=RunnerFilter(framework=['sast'], checks=['CKV3_SAST_11', 'seam-log-injection']),
                         external_checks_dir=[external_dir_checks], )

    bc_integration.bc_api_key = temp

    assert len(reports) == 0


def test_get_check_thresholds():
    prisma_engine = PrismaEngine()
    registry = Registry('')
    runner_filter = RunnerFilter()
    registry.runner_filter = runner_filter

    none = Severities[BcSeverities.NONE]
    medium = Severities[BcSeverities.MEDIUM]
    high = Severities[BcSeverities.HIGH]

    # test plain thresholds specified using --check and --skip-check, no enforcement rules
    assert prisma_engine.get_check_thresholds(registry) == (none, none)

    runner_filter.check_threshold = medium
    assert prisma_engine.get_check_thresholds(registry) == (medium, none)

    runner_filter.skip_check_threshold = medium
    assert prisma_engine.get_check_thresholds(registry) == (medium, medium)

    runner_filter.check_threshold = None
    assert prisma_engine.get_check_thresholds(registry) == (none, medium)

    # apply enforcement rules
    runner_filter.skip_check_threshold = None
    runner_filter.use_enforcement_rules = True
    runner_filter.enforcement_rule_configs = {
        CheckType.SAST: high
    }
    assert prisma_engine.get_check_thresholds(registry) == (high, none)

    # but --check and --skip-check with severities overrides enforcement rules
    runner_filter.check_threshold = medium
    assert prisma_engine.get_check_thresholds(registry) == (medium, none)

    runner_filter.skip_check_threshold = medium
    assert prisma_engine.get_check_thresholds(registry) == (medium, medium)

    runner_filter.check_threshold = None
    assert prisma_engine.get_check_thresholds(registry) == (none, medium)

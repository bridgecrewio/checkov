import pytest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.models.enums import CheckResult
from checkov.sast.consts import SastLanguages, SastEngines
from checkov.sast.engines.semgrep_engine import SemgrepEngine
from checkov.sast.runner import Runner
from checkov.runner_filter import RunnerFilter
import pathlib
import json
import os


def get_generic_ast_mock():
    return {'Pr': [{'ExprStmt': [{'Call': [{'N': {'Id': [['set_port',
                                                          {'token': {'OriginTok': {'str': 'set_port',
                                                                                   'charpos': 25,
                                                                                   'line': 2,
                                                                                   'column': 0,
                                                                                   'file': '/source_code/external_check/fail.py'}},
                                                           'transfo': 'NoTransfo'}],
                                                         {'id_info_id': 1,
                                                          'id_hidden': 'false',
                                                          'id_resolved': {'ref@': None},
                                                          'id_type': {'ref@': None},
                                                          'id_svalue': {'ref@': None}}]}},
                                           [{'token': {'OriginTok': {'str': '(',
                                                                     'charpos': 33,
                                                                     'line': 2,
                                                                     'column': 8,
                                                                     'file': '/source_code/external_check/fail.py'}},
                                             'transfo': 'NoTransfo'},
                                            [{'Arg': {'L': {'Int': [{'some': 443},
                                                                    {'token': {'OriginTok': {'str': '443',
                                                                                             'charpos': 34,
                                                                                             'line': 2,
                                                                                             'column': 9,
                                                                                             'file': '/source_code/external_check/fail.py'}},
                                                                     'transfo': 'NoTransfo'}]}}}],
                                            {'token': {'OriginTok': {'str': ')',
                                                                     'charpos': 37,
                                                                     'line': 2,
                                                                     'column': 12,
                                                                     'file': '/source_code/external_check/fail.py'}},
                                             'transfo': 'NoTransfo'}]]},
                                 {'token': {'FakeTokStr': ['', None]}, 'transfo': 'NoTransfo'}]},
                   {'ExprStmt': [{'Call': [{'N': {'Id': [['set_port',
                                                          {'token': {'OriginTok': {'str': 'set_port',
                                                                                   'charpos': 60,
                                                                                   'line': 4,
                                                                                   'column': 0,
                                                                                   'file': '/source_code/external_check/fail.py'}},
                                                           'transfo': 'NoTransfo'}],
                                                         {'id_info_id': 2,
                                                          'id_hidden': 'false',
                                                          'id_resolved': {'ref@': None},
                                                          'id_type': {'ref@': None},
                                                          'id_svalue': {'ref@': None}}]}},
                                           [{'token': {'OriginTok': {'str': '(',
                                                                     'charpos': 68,
                                                                     'line': 4,
                                                                     'column': 8,
                                                                     'file': '/source_code/external_check/fail.py'}},
                                             'transfo': 'NoTransfo'},
                                            [{'Arg': {'L': {'Int': [{'some': 8080},
                                                                    {'token': {'OriginTok': {'str': '8080',
                                                                                             'charpos': 69,
                                                                                             'line': 4,
                                                                                             'column': 9,
                                                                                             'file': '/source_code/external_check/fail.py'}},
                                                                     'transfo': 'NoTransfo'}]}}}],
                                            {'token': {'OriginTok': {'str': ')',
                                                                     'charpos': 73,
                                                                     'line': 4,
                                                                     'column': 13,
                                                                     'file': '/source_code/external_check/fail.py'}},
                                             'transfo': 'NoTransfo'}]]},
                                 {'token': {'FakeTokStr': ['', None]}, 'transfo': 'NoTransfo'}]}]}


def get_parsed_rule():
    return {'id': 'checks.temp_parsed_rules.CKV3_SAST_11', 'patterns': [{'pattern': 'set_port($ARG)'}, {
        'metavariable-comparison': {'metavariable': '$ARG', 'comparison': '$ARG < 1024'}}],
            'message': 'module setting superuser port', 'languages': ['python'], 'severity': 'INFO',
            'metadata': {'cwe': 'CWE-289: Authentication Bypass by Alternate Name', 'name': 'superuser port'}}


def test_sast_runner_python():
    runner = Runner()
    runner.registry.temp_semgrep_rules_path = os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                           'test_runner_python_temp_rules.yaml')
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


def test_sast_runner():
    runner = Runner()
    runner.registry.temp_semgrep_rules_path = os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                           'test_runner_temp_rules.yaml')
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


def test_get_generic_ast():
    cur_dir = pathlib.Path(__file__).parent.resolve()
    path = os.path.join(cur_dir, 'source_code', 'external_check', 'fail.py')
    result = SemgrepEngine._get_generic_ast(SastLanguages.PYTHON, path)
    result_json = json.dumps(result).replace(str(cur_dir), '')
    assert json.dumps(get_generic_ast_mock()) == result_json


def test_sast_prisma_runner_missing_key(mocker):
    mocker.patch("checkov.sast.engines.prisma_engine.PrismaEngine.run_go_library", return_value=[])
    mocker.patch("checkov.sast.engines.prisma_engine.PrismaEngine.setup_sast_artifact", return_value='')
    mocker.patch("checkov.sast.engines.prisma_engine.PrismaEngine.get_sast_artifact", return_value='')

    runner = Runner()
    runner.registry.temp_semgrep_rules_path = os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                           'test_runner_temp_rules.yaml')
    cur_dir = pathlib.Path(__file__).parent.resolve()
    source = os.path.join(cur_dir / 'source_code' / 'external_check')
    external_dir_checks = os.path.join(cur_dir, 'external_checks')
    reports = runner.run(source,
                         runner_filter=RunnerFilter(framework=['sast'], checks=['CKV3_SAST_11', 'seam-log-injection']),
                         external_checks_dir=[external_dir_checks], )

    assert len(reports) == 2
    assert runner.get_engine() == SastEngines.SEMGREP


@pytest.mark.skip(reason="This test should be an integration test")
def test_sast_prisma_runner(mocker):
    temp = bc_integration.bc_api_key
    bc_integration.bc_api_key = "123456"

    mocker.patch("checkov.sast.engines.prisma_engine.PrismaEngine.run_go_library", return_value=[])
    mocker.patch("checkov.sast.engines.prisma_engine.PrismaEngine.setup_sast_artifact", return_value='')
    mocker.patch("checkov.sast.engines.prisma_engine.PrismaEngine.get_sast_artifact", return_value='')

    runner = Runner()
    runner.registry.temp_semgrep_rules_path = os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                           'test_runner_temp_rules.yaml')
    cur_dir = pathlib.Path(__file__).parent.resolve()
    source = os.path.join(cur_dir / 'source_code' / 'external_check')
    external_dir_checks = os.path.join(cur_dir, 'external_checks')
    reports = runner.run(source,
                         runner_filter=RunnerFilter(framework=['sast'], checks=['CKV3_SAST_11', 'seam-log-injection']),
                         external_checks_dir=[external_dir_checks], )

    assert runner.get_engine() == SastEngines.PRISMA
    bc_integration.bc_api_key = temp

    assert len(reports) == 0

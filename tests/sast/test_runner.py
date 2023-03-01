from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.models.enums import CheckResult
from checkov.sast.consts import SastLanguages
from checkov.sast.runner import Runner
from semgrep.rule_match import RuleMatch
from semgrep.rule import Rule
from checkov.runner_filter import RunnerFilter
from semgrep.output import OutputSettings, OutputHandler
from semgrep.constants import OutputFormat, RuleSeverity
import semgrep.output_from_core as core
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
    runner.registry.temp_semgrep_rules_path = os.path.join(pathlib.Path(__file__).parent.resolve(), 'test_runner_python_temp_rules.yaml')
    source = os.path.join(pathlib.Path(__file__).parent.resolve(), 'source_code')
    reports = runner.run(source, runner_filter=RunnerFilter(framework=['sast_python']))

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


def test_sast_runner_get_semgrep_output():
    runner = Runner()
    runner.registry.temp_semgrep_rules_path = os.path.join(pathlib.Path(__file__).parent.resolve(), 'test_runner_get_semgrep_output_temp_rules.yaml')
    output_settings = OutputSettings(output_format=OutputFormat.JSON)
    output_handler = OutputHandler(output_settings)
    temp_semgrep_rules_path = pathlib.Path(__file__).parent / 'checks/temp_parsed_rules'
    source_dir = pathlib.Path(__file__).parent / 'source_code' / 'external_check'
    output = runner._get_semgrep_output([str(source_dir)], [str(temp_semgrep_rules_path)], output_handler)
    match = next(iter(output.matches.values()))
    assert match[0].match.location.path == f'{source_dir}/fail.py'
    assert match[0].match.location.start.line == 2
    assert match[0].match.location.end.line == 2
    assert match[0].severity == RuleSeverity.INFO
    assert match[0].rule_id.endswith('temp_parsed_rules.CKV_SAST_1')


def test_sast_runner_create_report():
    file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'source_code', 'python', 'SuperuserPort', 'fail.py')
    raw_rule = get_parsed_rule()
    rule = Rule(raw_rule)
    rule_match = core.CoreMatch(rule_id=core.RuleId(value='tests.sast.checks.CKV3_SAST_11'),
                                location=core.Location(path=file,
                                                       start=core.Position(line=1, col=1, offset=25),
                                                       end=core.Position(line=1, col=14, offset=38)),
                                extra=core.CoreMatchExtra(metavars=core.Metavars(value={'$ARG': core.MetavarValue(start=core.Position(line=2, col=10, offset=34), end=core.Position(line=2, col=13, offset=37), abstract_content='443', propagated_value=None)}),
                                                          message='module setting superuser port', dataflow_trace=None, rendered_fix=None, engine_kind=None))
    match = RuleMatch(match=rule_match,
                      severity=RuleSeverity.INFO,
                      fix=None,
                      fix_regex=None,
                      index=0,
                      match_based_index=0,
                      match_formula_string='$ARG $ARG < 1024 set_port($ARG)',
                      is_ignored=False,
                      message='module setting superuser port',
                      metadata=rule.metadata)
    runner = Runner()
    runner.registry.temp_semgrep_rules_path = os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                           'test_runner_create_report_temp_rules.yaml')
    report = runner._create_report(SastLanguages.PYTHON.value, [match])
    assert report.check_type == CheckType.SAST_PYTHON
    assert len(report.failed_checks) == 1
    assert report.failed_checks[0].check_id == 'CKV3_SAST_11'
    assert report.failed_checks[0].severity.name == 'LOW'
    assert report.failed_checks[0].file_path == 'fail.py'
    assert report.failed_checks[0].check_name == 'superuser port'
    assert report.failed_checks[0].code_block == [(1, 'set_port(443)\n')]
    assert report.failed_checks[0].file_abs_path == file
    assert report.failed_checks[0].file_line_range == [1, 1]
    assert report.failed_checks[0].check_result.get('result') == CheckResult.FAILED


def test_sast_runner_get_code_block():
    runner = Runner()
    lines = ['a', 'b', 'c', 'd']
    result = runner._get_code_block(lines, 2)
    assert result == [(2, 'a'), (3, 'b'), (4, 'c'), (5, 'd')]


def test_sast_runner():
    runner = Runner()
    runner.registry.temp_semgrep_rules_path = os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                           'test_runner_temp_rules.yaml')
    cur_dir = pathlib.Path(__file__).parent.resolve()
    source = os.path.join(cur_dir / 'source_code' / 'external_check')
    external_dir_checks = os.path.join(cur_dir, 'external_checks')
    reports = runner.run(source,
                         runner_filter=RunnerFilter(framework=['sast'], checks=['CKV3_SAST_11', 'seam-log-injection']),
                         external_checks_dir=[external_dir_checks],)
    assert len(reports) == 2
    python_report = reports[0]
    assert python_report.check_type == CheckType.SAST_PYTHON
    assert len(python_report.failed_checks) == 1
    assert python_report.failed_checks[0].check_id == 'CKV3_SAST_11'
    assert python_report.failed_checks[0].severity.name == 'MEDIUM'
    assert python_report.failed_checks[0].file_path == 'fail.py'
    assert python_report.failed_checks[0].check_name == 'Ensure superuser port is not set'
    assert python_report.failed_checks[0].code_block == [(2, 'set_port(443)\n')]
    assert python_report.failed_checks[0].file_abs_path == os.path.join(source, 'fail.py')
    assert python_report.failed_checks[0].file_line_range == [2, 2]
    assert python_report.failed_checks[0].check_result.get('result') == CheckResult.FAILED

    java_report = reports[1]
    assert len(java_report.failed_checks) == 2
    assert java_report.failed_checks[0].check_id == 'seam-log-injection'
    assert java_report.failed_checks[0].severity.name == 'HIGH'
    assert java_report.failed_checks[0].file_path == 'fail.java'
    assert java_report.failed_checks[0].check_name == 'seam log injection'
    assert java_report.failed_checks[0].code_block == [(31, 'log.info("request: method="+httpRequest.getMethod()+", URL="+httpRequest.getRequestURI());\n')]
    assert java_report.failed_checks[0].file_abs_path == os.path.join(source, 'fail.java')
    assert java_report.failed_checks[0].file_line_range == [31, 31]
    assert java_report.failed_checks[0].check_result.get('result') == CheckResult.FAILED

    assert java_report.failed_checks[1].check_id == 'seam-log-injection'
    assert java_report.failed_checks[1].severity.name == 'HIGH'
    assert java_report.failed_checks[1].file_path == 'fail.java'
    assert java_report.failed_checks[1].check_name == 'seam log injection'
    assert java_report.failed_checks[1].code_block == [(40, 'log.info("Current logged in user : " + user.getUsername());\n')]
    assert java_report.failed_checks[1].file_abs_path == os.path.join(source, 'fail.java')
    assert java_report.failed_checks[1].file_line_range == [40, 40]
    assert java_report.failed_checks[1].check_result.get('result') == CheckResult.FAILED


def test_code_block_cut_ident():
    code_block = [(1, '    def func():'), [2, '        hi = 0']]
    code_block_cut_ident = Runner._cut_code_block_ident(code_block)
    assert code_block_cut_ident[0][0] == 1
    assert code_block_cut_ident[0][1] == 'def func():'
    assert code_block_cut_ident[1][0] == 2
    assert code_block_cut_ident[1][1] == '    hi = 0'


def test_get_generic_ast():
    cur_dir = pathlib.Path(__file__).parent.resolve()
    path = os.path.join(cur_dir, 'source_code', 'external_check', 'fail.py')
    result = Runner._get_generic_ast(SastLanguages.PYTHON, path)
    result_json = json.dumps(result).replace(str(cur_dir), '')
    assert json.dumps(get_generic_ast_mock()) == result_json

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
             'file': '/source_code/file.py'}},
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
          'file': '/source_code/file.py'}},
        'transfo': 'NoTransfo'},
       [{'Arg': {'L': {'Int': [{'some': 443},
            {'token': {'OriginTok': {'str': '443',
               'charpos': 34,
               'line': 2,
               'column': 9,
               'file': '/source_code/file.py'}},
             'transfo': 'NoTransfo'}]}}}],
       {'token': {'OriginTok': {'str': ')',
          'charpos': 37,
          'line': 2,
          'column': 12,
          'file': '/source_code/file.py'}},
        'transfo': 'NoTransfo'}]]},
    {'token': {'FakeTokStr': ['', None]}, 'transfo': 'NoTransfo'}]},
  {'ExprStmt': [{'Call': [{'N': {'Id': [['set_port',
          {'token': {'OriginTok': {'str': 'set_port',
             'charpos': 60,
             'line': 4,
             'column': 0,
             'file': '/source_code/file.py'}},
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
          'file': '/source_code/file.py'}},
        'transfo': 'NoTransfo'},
       [{'Arg': {'L': {'Int': [{'some': 8080},
            {'token': {'OriginTok': {'str': '8080',
               'charpos': 69,
               'line': 4,
               'column': 9,
               'file': '/source_code/file.py'}},
             'transfo': 'NoTransfo'}]}}}],
       {'token': {'OriginTok': {'str': ')',
          'charpos': 73,
          'line': 4,
          'column': 13,
          'file': '/source_code/file.py'}},
        'transfo': 'NoTransfo'}]]},
    {'token': {'FakeTokStr': ['', None]}, 'transfo': 'NoTransfo'}]}]}


def get_raw_rule():
    return {'id': 'tests.sast.checks.CKV_SAST_1', 'patterns': [{'pattern': 'set_port($ARG)'}, {
        'metavariable-comparison': {'metavariable': '$ARG', 'comparison': '$ARG < 1024'}}],
                'message': 'module setting superuser port', 'languages': ['python'], 'severity': 'INFO',
                'metadata': {'cwe': ['CWE-289: Authentication Bypass by Alternate Name'], 'name': 'superuser port',
                             'category': 'security', 'technology': ['gorilla'], 'confidence': 'MEDIUM',
                             'license': 'Commons Clause License Condition v1.0[LGPL-2.1-only]',
                             'references': ['https://cwe.mitre.org/data/definitions/289.html'],
                             'subcategory': ['audit'], 'impact': 'MEDIUM', 'likelihood': 'LOW'}}


def test_sast_runner_python():
    runner = Runner()
    source = os.path.join(pathlib.Path(__file__).parent.resolve(), 'source_code')
    report = runner.run(source, runner_filter=RunnerFilter(framework=['sast_python']))
    assert report.check_type == CheckType.SAST
    assert len(report.failed_checks) == 1
    assert report.failed_checks[0].check_id == 'CKV_SAST_1'
    assert report.failed_checks[0].severity.name == 'LOW'
    assert report.failed_checks[0].file_path == 'file.py'
    assert report.failed_checks[0].check_name == 'superuser port'
    assert report.failed_checks[0].code_block == [(2, 'set_port(443)\n')]
    assert report.failed_checks[0].file_abs_path == os.path.join(source, 'file.py')
    assert report.failed_checks[0].file_line_range == [2, 2]
    assert report.failed_checks[0].check_result.get('result') == CheckResult.FAILED


def test_sast_runner_get_semgrep_output():
    runner = Runner()
    output_settings = OutputSettings(output_format=OutputFormat.JSON)
    output_handler = OutputHandler(output_settings)
    checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'checks')
    source_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'source_code')
    output = runner._get_semgrep_output([source_dir], [checks_dir], output_handler)
    raw_rule = get_raw_rule()
    rule = Rule(raw=raw_rule)
    assert output.matches[rule][0].match.location.path == f'{source_dir}/file.py'
    assert output.matches[rule][0].match.location.start.line == 2
    assert output.matches[rule][0].match.location.end.line == 2
    assert output.matches[rule][0].severity == RuleSeverity.INFO
    assert output.matches[rule][0].rule_id == 'tests.sast.checks.CKV_SAST_1'


def test_sast_runner_create_report():
    file = os.path.join(pathlib.Path(__file__).parent.resolve(), 'source_code', 'file.py')
    raw_rule = get_raw_rule()
    rule = Rule(raw_rule)
    rule_match = core.CoreMatch(rule_id=core.RuleId(value='tests.sast.checks.CKV_SAST_1'),
                                location=core.Location(path=file,
                                                       start=core.Position(line=2, col=1, offset=25),
                                                       end=core.Position(line=2, col=14, offset=38)),
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
                      message='module setting superuser port')
    filtered_matches_by_rule = {rule: [match]}
    runner = Runner()
    report = runner._create_report(filtered_matches_by_rule)
    assert report.check_type == CheckType.SAST
    assert len(report.failed_checks) == 1
    assert report.failed_checks[0].check_id == 'CKV_SAST_1'
    assert report.failed_checks[0].severity.name == 'LOW'
    assert report.failed_checks[0].file_path == 'file.py'
    assert report.failed_checks[0].check_name == 'superuser port'
    assert report.failed_checks[0].code_block == [(2, 'set_port(443)\n')]
    assert report.failed_checks[0].file_abs_path == file
    assert report.failed_checks[0].file_line_range == [2, 2]
    assert report.failed_checks[0].check_result.get('result') == CheckResult.FAILED


def test_sast_runner_get_code_block():
    runner = Runner()
    lines = ['a', 'b', 'c', 'd']
    result = runner._get_code_block(lines, 2)
    assert result == [(2, 'a'), (3, 'b'), (4, 'c'), (5, 'd')]


def test_sast_runner():
    runner = Runner()
    cur_dir = pathlib.Path(__file__).parent.resolve()
    source = os.path.join(cur_dir, 'source_code')
    external_dir_checks = os.path.join(cur_dir, 'external_checks')
    report = runner.run(source, runner_filter=RunnerFilter(framework=['sast']), external_checks_dir=[external_dir_checks])
    assert report.check_type == CheckType.SAST
    assert len(report.failed_checks) == 3
    assert report.failed_checks[0].check_id == 'CKV_SAST_1'
    assert report.failed_checks[0].severity.name == 'LOW'
    assert report.failed_checks[0].file_path == 'file.py'
    assert report.failed_checks[0].check_name == 'superuser port'
    assert report.failed_checks[0].code_block == [(2, 'set_port(443)\n')]
    assert report.failed_checks[0].file_abs_path == os.path.join(source, 'file.py')
    assert report.failed_checks[0].file_line_range == [2, 2]
    assert report.failed_checks[0].check_result.get('result') == CheckResult.FAILED

    assert report.failed_checks[1].check_id == 'seam-log-injection'
    assert report.failed_checks[1].severity.name == 'HIGH'
    assert report.failed_checks[1].file_path == 'file.java'
    assert report.failed_checks[1].check_name == 'seam log injection'
    assert report.failed_checks[1].code_block == [(31, 'log.info("request: method="+httpRequest.getMethod()+", URL="+httpRequest.getRequestURI());\n')]
    assert report.failed_checks[1].file_abs_path == os.path.join(source, 'file.java')
    assert report.failed_checks[1].file_line_range == [31, 31]
    assert report.failed_checks[1].check_result.get('result') == CheckResult.FAILED

    assert report.failed_checks[2].check_id == 'seam-log-injection'
    assert report.failed_checks[2].severity.name == 'HIGH'
    assert report.failed_checks[2].file_path == 'file.java'
    assert report.failed_checks[2].check_name == 'seam log injection'
    assert report.failed_checks[2].code_block == [(40, 'log.info("Current logged in user : " + user.getUsername());\n')]
    assert report.failed_checks[2].file_abs_path == os.path.join(source, 'file.java')
    assert report.failed_checks[2].file_line_range == [40, 40]
    assert report.failed_checks[2].check_result.get('result') == CheckResult.FAILED


def test_code_block_cut_ident():
    code_block = [(1, '    def func():'), [2, '        hi = 0']]
    code_block_cut_ident = Runner._cut_code_block_ident(code_block)
    assert code_block_cut_ident[0][0] == 1
    assert code_block_cut_ident[0][1] == 'def func():'
    assert code_block_cut_ident[1][0] == 2
    assert code_block_cut_ident[1][1] == '    hi = 0'


def test_get_generic_ast():
    cur_dir = pathlib.Path(__file__).parent.resolve()
    path = os.path.join(cur_dir, 'source_code', 'file.py')
    result = Runner._get_generic_ast(SastLanguages.PYTHON, path)
    result_json = json.dumps(result).replace(str(cur_dir), '')
    assert json.dumps(get_generic_ast_mock()) == result_json


def test_sast_skip_checks():
    runner = Runner()
    cur_dir = pathlib.Path(__file__).parent.resolve()
    source = os.path.join(cur_dir, 'source_code')
    external_dir_checks = os.path.join(cur_dir, 'external_checks')
    report = runner.run(source, runner_filter=RunnerFilter(framework=['sast'], skip_checks=['CKV_SAST_1']), external_checks_dir=[external_dir_checks])
    assert report.check_type == CheckType.SAST
    assert len(report.failed_checks) > 0
    assert 'CKV_SAST_1' not in [check.check_id for check in report.failed_checks]

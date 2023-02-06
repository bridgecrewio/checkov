from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.models.enums import CheckResult
from checkov.sast.runner import Runner
from semgrep.rule_match import RuleMatch
from semgrep.rule import Rule
from checkov.runner_filter import RunnerFilter
from semgrep.output import OutputSettings, OutputHandler
from semgrep.constants import OutputFormat, RuleSeverity
import semgrep.output_from_core as core
import pathlib
import os


def test_sast_runner_python():
    checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'checks')
    runner = Runner()
    source = os.path.join(pathlib.Path(__file__).parent.resolve(), 'source_code')
    report = runner.run(source, runner_filter=RunnerFilter(framework=['sast_python']))
    assert report.check_type == CheckType.SAST
    assert len(report.failed_checks) == 1
    assert report.failed_checks[0].check_id == 'CKV_SAST_1'
    assert report.failed_checks[0].severity.name == 'LOW'
    assert report.failed_checks[0].file_path == 'bb.py'
    assert report.failed_checks[0].check_name == 'superuser port'
    assert report.failed_checks[0].code_block == [(2, 'set_port(443)\n')]
    assert report.failed_checks[0].file_abs_path == os.path.join(source, 'bb.py')
    assert report.failed_checks[0].file_line_range == [2, 2]
    assert report.failed_checks[0].check_result.get('result') == CheckResult.FAILED


def test_sast_runner_get_semgrep_output():
    runner = Runner()
    output_settings = OutputSettings(output_format=OutputFormat.JSON)
    output_handler = OutputHandler(output_settings)
    checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'checks')
    source_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'source_code')
    output = runner._get_semgrep_output([source_dir], [checks_dir], output_handler)
    a = 0


def test_sast_runner_create_report():
    raw_rule = {'id': 'checkov.sast.checks.rules.python.CKV_SAST_1', 'patterns': [{'pattern': 'set_port($ARG)'}, {'metavariable-comparison': {'metavariable': '$ARG', 'comparison': '$ARG < 1024'}}], 'message': 'module setting superuser port', 'languages': ['python'], 'severity': 'INFO', 'metadata': {'cwe': ['CWE-289: Authentication Bypass by Alternate Name'], 'name': 'superuser port', 'category': 'security', 'technology': ['gorilla'], 'confidence': 'MEDIUM', 'license': 'Commons Clause License Condition v1.0[LGPL-2.1-only]', 'references': ['https://cwe.mitre.org/data/definitions/289.html'], 'subcategory': ['audit'], 'impact': 'MEDIUM', 'likelihood': 'LOW'}}
    rule = Rule(raw_rule)
    rule_match = core.CoreMatch(rule_id=core.RuleId(value='checkov.sast.checks.rules.python.CKV_SAST_1'),
                                location=core.Location(path='/Users/arosenfeld/Desktop/fff/bb.py',
                                                       start=core.Position(line=2, col=1, offset=25),
                                                       end=core.Position(line=2, col=14, offset=38)),
                                extra=core.CoreMatchExtra(metavars=core.Metavars(value={'$ARG': core.MetavarValue(start=core.Position(line=2, col=10, offset=34), end=core.Position(line=2, col=13, offset=37), abstract_content='443', propagated_value=None)}),
                                                          message='module setting superuser port', dataflow_trace=None, rendered_fix=None))
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
    assert report.failed_checks[0].file_path == 'bb.py'
    assert report.failed_checks[0].check_name == 'superuser port'
    assert report.failed_checks[0].code_block == [(2, 'set_port(443)\n')]
    assert report.failed_checks[0].file_abs_path == '/Users/arosenfeld/Desktop/fff/bb.py'
    assert report.failed_checks[0].file_line_range == [2, 2]
    assert report.failed_checks[0].check_result.get('result') == CheckResult.FAILED
    

def test_sast_runner_get_code_block():
    runner = Runner()
    lines = ['a', 'b', 'c', 'd']
    result = runner._get_code_block(lines, 2)
    assert result == [(2, 'a'), (3, 'b'), (4, 'c'), (5, 'd')]


def test_sast_runner():
    checks_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'checks')
    runner = Runner()
    source = os.path.join(pathlib.Path(__file__).parent.resolve(), 'source_code')
    external_dir_checks = os.path.join(pathlib.Path(__file__).parent.resolve(), 'external_checks')
    report = runner.run(source, runner_filter=RunnerFilter(framework=['sast']), external_checks_dir=[external_dir_checks])
    assert report.check_type == CheckType.SAST
    assert len(report.failed_checks) == 3
    assert report.failed_checks[0].check_id == 'CKV_SAST_1'
    assert report.failed_checks[0].severity.name == 'LOW'
    assert report.failed_checks[0].file_path == 'bb.py'
    assert report.failed_checks[0].check_name == 'superuser port'
    assert report.failed_checks[0].code_block == [(2, 'set_port(443)\n')]
    assert report.failed_checks[0].file_abs_path == os.path.join(source, 'bb.py')
    assert report.failed_checks[0].file_line_range == [2, 2]
    assert report.failed_checks[0].check_result.get('result') == CheckResult.FAILED

    assert report.failed_checks[1].check_id == 'seam-log-injection'
    assert report.failed_checks[1].severity.name == 'HIGH'
    assert report.failed_checks[1].file_path == 'aa.java'
    assert report.failed_checks[1].check_name == 'seam log injection'
    assert report.failed_checks[1].code_block == [(31, '                log.info("request: method="+httpRequest.getMethod()+", URL="+httpRequest.getRequestURI());\n')]
    assert report.failed_checks[1].file_abs_path == os.path.join(source, 'aa.java')
    assert report.failed_checks[1].file_line_range == [31, 31]
    assert report.failed_checks[1].check_result.get('result') == CheckResult.FAILED

    assert report.failed_checks[2].check_id == 'seam-log-injection'
    assert report.failed_checks[2].severity.name == 'HIGH'
    assert report.failed_checks[2].file_path == 'aa.java'
    assert report.failed_checks[2].check_name == 'seam log injection'
    assert report.failed_checks[2].code_block == [(40, '        log.info("Current logged in user : " + user.getUsername());\n')]
    assert report.failed_checks[2].file_abs_path == os.path.join(source, 'aa.java')
    assert report.failed_checks[2].file_line_range == [40, 40]
    assert report.failed_checks[2].check_result.get('result') == CheckResult.FAILED
    

def test_code_block_cut_ident():
    code_block = [(1, '    def aa():'), [2, '        hi = 0']]
    code_block_cut_ident = Runner._cut_code_block_ident(code_block)
    assert code_block_cut_ident[0][0] == 1
    assert code_block_cut_ident[0][1] == 'def aa():'
    assert code_block_cut_ident[1][0] == 2
    assert code_block_cut_ident[1][1] == '    hi = 0'

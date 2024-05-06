from __future__ import annotations

from checkov.common.sast.consts import SastLanguages
from checkov.sast.engines.prisma_engine import PrismaEngine
from checkov.sast.record import SastRecord
from checkov.sast.report import SastData, SastReport
from checkov.common.sast.report_types import Function, PrismaReport, Repositories, File, Package, Point, MatchLocation, \
    DataFlow, MatchMetadata, RuleMatch, Match, SkippedCheck, RuleMatchMetadata


def _create_sast_reports_for_test_get_sast_reachability_report_with_one_report() -> list[SastReport]:
    # we don't care about the init's params, except for the sast-language
    report1 = SastReport('', {}, SastLanguages.JAVASCRIPT, PrismaReport(rule_match={}, errors={}, profiler={},
                                                                        run_metadata={}, imports={},
                                                                        reachability_report={},
                                                                        skipped_checks_by_file={}))
    report1.sast_reachability = {
        'repo_1': Repositories(files={
            '/index.js': File(packages={
                'axios': Package(alias='ax', functions=[
                    Function(name='trim', alias='hopa', line_number=4, code_block='hopa()', cve_id='cve-11')
                ]),
                'lodash': Package(alias='', functions=[
                    Function(name='template', alias='', line_number=1, code_block='template()', cve_id='cve-11'),
                    Function(name='toNumber', alias='', line_number=4, code_block='hopa()', cve_id='cve-11')
                ])
            }),
            '/main.js': File(packages={
                'axios': Package(alias='ax', functions=[
                    Function(name='trim', alias='hi', line_number=4, code_block='hi()', cve_id='cve-11')
                ])
            })
        })
    }
    return [report1]


def test_get_sast_reachability_report_with_one_report():
    scan_reports: list[SastReport] = _create_sast_reports_for_test_get_sast_reachability_report_with_one_report()
    sast_reachability_report = SastData.get_sast_reachability_report(scan_reports)
    assert sast_reachability_report == {
        'reachability': {
            SastLanguages.JAVASCRIPT: {
                '/index.js': File(packages={
                    'axios': Package(alias='ax', functions=[
                        Function(name='trim', alias='hopa', line_number=4, code_block='hopa()', cve_id='cve-11')
                    ]),
                    'lodash': Package(alias='', functions=[
                        Function(name='template', alias='', line_number=1, code_block='template()', cve_id='cve-11'),
                        Function(name='toNumber', alias='', line_number=4, code_block='hopa()', cve_id='cve-11')
                    ])
                }),
                '/main.js': File(packages={
                    'axios': Package(alias='ax', functions=[
                        Function(name='trim', alias='hi', line_number=4, code_block='hi()', cve_id='cve-11')
                    ])
                })
            }
        }
    }


def test_get_code_lines_taint():
    record = SastRecord(check_id='', check_name='', resource='', evaluations={},
                        check_class='', check_result=None, code_block=[], file_path='', file_line_range=[],
                        metadata=MatchMetadata(taint_mode=DataFlow(data_flow=[MatchLocation(path='checkov/arosenfeld6666/arosenfeld6666_abc/aaa/1706717499988/src/file_that_import.js', start=Point(row=3, column=0), end=Point(row=3, column=32), code_block='let password = request.password;'), MatchLocation(path='checkov/arosenfeld6666/arosenfeld6666_abc/aaa/1706717499988/src/file_that_import.js', start=Point(row=6, column=0), end=Point(row=6, column=17), code_block='Danger(password);'), MatchLocation(path='checkov/arosenfeld6666/arosenfeld6666_abc/aaa/1706717499988/src/imported_file.js', start=Point(row=2, column=4), end=Point(row=2, column=38), code_block='console.log("Danger: " + password)')])),
                        file_abs_path='', severity=None, cwe='',
                        owasp='', show_severity=True)

    code_lines_actual_output, file_details_actual_output = record.get_code_lines_taint(record.metadata.taint_mode.data_flow)
    code_lines_expected_output = '\t\tfile_that_import.js\n\t\t\x1b[37m3 | \x1b[33mlet password = request.password;\n\t\t...\n\t\t\x1b[37m6 | \x1b[33mDanger(password);\n\t\timported_file.js\n\t\t\x1b[37m2 | \x1b[33mconsole.log("Danger: " + password)\n'
    file_details_expected_output = 'file_that_import.js->3->6->imported_file.js->2'
    assert code_lines_expected_output == code_lines_actual_output
    assert file_details_expected_output == file_details_actual_output


def test_skipped_checks():
    report = PrismaReport(rule_match={
        SastLanguages.PYTHON: {'CKV3_SAST_11': RuleMatch(
            check_id='CKV3_SAST_11', check_name='Use of module setting superuser port',
            check_cwe=['CWE-289: Authentication Bypass by Alternate Name'], severity='LOW', check_owasp=None,
            metadata=RuleMatchMetadata(), matches=[
                Match(exact_hash='e97a01a1cb2abee84ad113d828f8d500eccb150941200fd6df9356bb9c193604',
                      structure_hash='8e63ba7c140643381a68470a5d9296e6290999e3fc70971e860480c0bc24a474',
                      location=MatchLocation(
                          path='tests/python/src/simple_within.py',
                          start=Point(row=2, column=0), end=Point(row=2, column=11), code_block='set_port(1)'),
                      metadata=MatchMetadata(taint_mode=None, code_locations=None),
                      minimized_ast='{"type":"module","children":[{"type":"expression_statement","children":[{"type":"call","name":"set_port","children":[{"type":"identifier"},{"type":"argument_list","children":[{"type":"integer"}]}]}]}]}')])}
    }, errors={}, profiler={}, run_metadata={}, imports={}, reachability_report={}, skipped_checks_by_file={
        'tests/python/src/simple_within.py': [SkippedCheck(check_id='CKV3_SAST_11', suppress_comment="Don't feel like it")]
    })
    prisma_engine = PrismaEngine()
    prisma_engine.enable_inline_suppressions = True
    sast_report = prisma_engine.create_report(report)
    assert len(sast_report[0].failed_checks) == 0 and len(sast_report[0].skipped_checks) == 1
    assert sast_report[0].skipped_checks[0].check_result['suppress_comment'] == "Don't feel like it"

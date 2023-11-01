from __future__ import annotations

from checkov.common.sast.consts import SastLanguages
from checkov.sast.report import SastData, SastReport
from checkov.sast.prisma_models.report import Function, Repositories, File, Package


def _create_sast_reports_for_test_get_sast_reachability_report_with_one_report() -> list[SastReport]:
    # we don't care about the init's params, except for the sast-language
    report1 = SastReport('', {}, SastLanguages.JAVASCRIPT)
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
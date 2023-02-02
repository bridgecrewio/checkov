from __future__ import annotations

import logging
from enum import Enum
from typing import Dict, Any

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report

from checkov.common.runners.base_post_runner import BasePostRunner
from checkov.common.util.type_forcers import force_list
from checkov.policies_3d.record import Policy3dRecord
from checkov.policies_3d.checks_infra.base_check import Base3dPolicyCheck
from checkov.runner_filter import RunnerFilter


class CVECheckAttribute(str, Enum):
    RISK_FACTORS = "risk_factors"


class CVEReportAttribute(str, Enum):
    RISK_FACTORS = 'riskFactors'


CVE_CHECK_TO_REPORT_ATTRIBUTE = {
    CVECheckAttribute.RISK_FACTORS: CVEReportAttribute.RISK_FACTORS
}


class Policy3dRunner(BasePostRunner):
    check_type = CheckType.POLICY_3D  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__()

    def run(  # type:ignore[override]
            self,
            checks: list[Base3dPolicyCheck] | None = None,
            scan_reports: list[Report] | None = None,
            runner_filter: RunnerFilter | None = None
    ) -> Report:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        report = Report(self.check_type)

        if not checks or not scan_reports:
            logging.debug("No checks or reports scan.")
            return report

        self.pbar.initiate(len(checks))

        reports_by_framework = {report.check_type: report for report in scan_reports}
        for check in checks:
            records = self.collect_check(check, reports_by_framework)
            for record in records:
                report.add_record(record=record)

        self.pbar.close()
        return report

    def collect_check(self, check: Base3dPolicyCheck, reports_by_fw: dict[str, Report]) -> list[Policy3dRecord]:
        records = []
        iac_results_map = self.solve_check_iac(check, reports_by_fw)
        cve_results_map = self.solve_check_cve(check, reports_by_fw)

        for iac_resource, iac_records in iac_results_map.items():
            for cve_resource, vulnerabilities in cve_results_map.items():
                if iac_resource == cve_resource:
                    # This means we found the combination on the same resource -> create a violation for that resource
                    check_result = CheckResult.FAILED
                    iac_records = [record for record in iac_records]
                    record = self.get_record(check, iac_records[0], vulnerabilities, check_result, iac_records)
                    record.set_guideline(check.guideline)
                    records.append(record)

        self.pbar.update()
        return records

    def solve_check_iac(self, check: Base3dPolicyCheck, reports_by_fw: dict[str, Report]) -> dict[str, list[Record]]:
        iac_results_map: dict[str, list[Record]] = {}
        if check.iac:
            for framework, bc_check_ids in check.iac.items():
                framework_report = reports_by_fw.get(framework)
                if framework_report:
                    fw_records = framework_report.failed_checks
                    for record in fw_records:
                        if record.bc_check_id in bc_check_ids:
                            resource_id = f'{record.file_abs_path}:{record.resource}'
                            if resource_id in iac_results_map:
                                iac_results_map[resource_id].append(record)
                            else:
                                iac_results_map[resource_id] = [record]

                    # the following implements the AND logic for the list of iac expected check ids
                    for resource in list(iac_results_map.keys()):
                        if len(iac_results_map[resource]) != len(bc_check_ids):
                            del iac_results_map[resource]

        return iac_results_map

    def solve_check_cve(self, check: Base3dPolicyCheck, reports_by_fw: dict[str, Report]) -> dict[str, list[Dict[str, Any]]]:
        cve_results_map: dict[str, list[Dict[str, Any]]] = {}
        if check.cve:
            cve_report = reports_by_fw.get(CheckType.SCA_IMAGE)
            if cve_report:
                image_results = cve_report.image_cached_results
                for attribute, value in check.cve.items():
                    for image_result in image_results:
                        matching_cves = [vuln for vuln in image_result.get('vulnerabilities', []) if
                                         value[0] in force_list(vuln.get(CVE_CHECK_TO_REPORT_ATTRIBUTE[attribute], []))]
                        if matching_cves:
                            image_related_resource = image_result.get('relatedResourceId')
                            image_name = image_result.get('dockerImageName')
                            if not image_related_resource or not image_name:
                                logging.debug(
                                    "[policies3d/runner](solve_check_cve) Found vulnerabilities of an image without a related resource or image name, skipping")
                                break
                            for cve in matching_cves:
                                cve['dockerImageName'] = image_name
                            # The current logic for multiple cve conditions in the policy is of "OR" - we add all of
                            # the matching cves, even if matched only by a single policy attribute. To implement an
                            # "AND" logic for the combination of conditions, the matching cves need to be filtered
                            # before being added to the result.
                            if image_related_resource in cve_results_map:
                                cve_results_map[image_related_resource].extend(matching_cves)
                            else:
                                cve_results_map[image_related_resource] = matching_cves
        return cve_results_map

    def get_record(self, check: Base3dPolicyCheck, iac_record: Record, vulnerabilities: list[Dict[str, Any]],
                   check_result: CheckResult, iac_records: list[Record]) -> Policy3dRecord:
        return Policy3dRecord(
            check_id=check.id,
            bc_check_id=check.bc_id,
            check_name=check.name,
            check_result={'result': check_result},
            code_block=iac_record.code_block,
            file_path=iac_record.file_path,
            file_line_range=iac_record.file_line_range,
            resource=f'{iac_record.file_path}:{iac_record.resource}',
            evaluations=None,
            check_class=check.__class__.__module__,
            file_abs_path=iac_record.file_abs_path,
            severity=check.severity,
            vulnerabilities=vulnerabilities,
            iac_records=iac_records
        )

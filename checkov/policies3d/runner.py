from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report

# Import of the checks registry for a specific resource type
from checkov.common.graph.checks_infra.registry import BaseRegistry

from checkov.common.runners.base_post_runner import BasePostRunner
from checkov.common.util.type_forcers import force_list
from checkov.policies3d.checks_infra.base_check import Base3dPolicyCheck
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Policy3dRunner(BasePostRunner):
    check_type = CheckType.POLICY_3D  # type:ignore[attr-defined]  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__()

    def run(
            self,
            checks: list[Base3dPolicyCheck] | None = None,
            scan_reports: list[Report] | None = None,
            runner_filter: RunnerFilter | None = None
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        report = Report(self.check_type)

        if not checks or not scan_reports:
            logging.debug("No checks or reports scan.")
            return report

        self.pbar.initiate(len(checks))

        reports_by_fw = {report.check_type: report for report in scan_reports}
        for check in checks:
            record = self.run_check(check, reports_by_fw)
            record.set_guideline(check.guideline)
            report.add_record(record=record)

        self.pbar.close()

        return report

    def run_check(self, check: Base3dPolicyCheck, reports_by_fw: dict) -> Record:
        check_result = CheckResult.PASSED
        record_rel_file_path = ''
        record_abs_file_path = ''
        record_code_block = ''
        record_line_range = [-1, -1]
        record_resource = ''

        cve_results_map = {}
        if check.cve:
            cve_report = reports_by_fw.get('sca_image')
            if cve_report:
                image_results = cve_report.image_cached_results
                # extract what's need to be checked
                risk_factor = None
                for attribute, value in check.cve.items():
                    if attribute == 'risk_factors':
                        risk_factor = value[0]

                # get all relevant cve scan reports
                if risk_factor:
                    for image in image_results:
                        relevant_vulns = [vuln for vuln in image.get('vulnerabilities', []) if
                                          risk_factor in force_list(vuln.get('riskFactors', []))]
                        if relevant_vulns:
                            image_related_resource = image.get('relatedResourceId')
                            if image_related_resource in cve_results_map:
                                cve_results_map[image_related_resource].extend(relevant_vulns)
                            else:
                                cve_results_map[image_related_resource] = relevant_vulns
        iac_results_map = {}
        if check.iac:
            # extract what's need to be checked
            for fw, bc_check_ids in check.iac.items():
                fw_report = reports_by_fw.get(fw)
                if fw_report:
                    fw_records = fw_report.failed_checks
                    for record in fw_records:
                        if record.bc_check_id in bc_check_ids:
                            resource_id = f'{record.file_abs_path}:{record.resource}'
                            if resource_id in iac_results_map:
                                iac_results_map[resource_id].append(record)
                            else:
                                iac_results_map[resource_id] = [record]

        # create the final result
        for iac_resource in iac_results_map:
            for cve_resource in cve_results_map:
                if iac_resource == cve_resource:
                    check_result = CheckResult.FAILED
                    print(iac_resource)

        record = Record(
            check_id=check.id,
            bc_check_id=check.bc_id,
            check_name=check.name,
            check_result={'result': check_result},
            code_block=record_code_block,
            file_path=record_rel_file_path,
            file_line_range=record_line_range,
            resource=record_resource,
            # type:ignore[arg-type]  # key is str not BaseCheck
            evaluations=None,
            check_class=check.__class__.__module__,
            file_abs_path=record_abs_file_path,
            entity_tags=None,
            severity=check.severity,
        )
        self.pbar.update()
        return record


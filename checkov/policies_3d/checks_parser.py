from __future__ import annotations

from typing import Dict, Any

from checkov.common.output.record import Record
from checkov.policies_3d.checks_infra.base_parser import Base3dPolicyCheckParser
from checkov.policies_3d.checks_infra.base_check import Base3dPolicyCheck
from checkov.policies_3d.syntax.syntax import Predicament, RiskFactorCVEContains
from checkov.sca_image.models import ReportCVE

SUPPORTED_LOGICAL_OPERATORS = ['and', 'or']
CVE_ATTRIBUTE_TO_PREDICATE_CLASS = {'risk_factors': RiskFactorCVEContains}
SCA_CHECK_ID_PREFIXES = ['CKV_CVE_', 'BC_LIC_1', 'BC_LIC_2']
SECRETS_CHECK_ID_PREFIXES = ['BC_GIT_']

class Policy3dParser(Base3dPolicyCheckParser):
    def __init__(self, raw_check: dict[str, dict[str, Any]] | None = None,
                 resource: str | None = None, records: list[Record] | None = None):
        super().__init__(raw_check)
        self.resource = resource
        self.records = records

    def parse_raw_check(self, raw_check: Dict[str, Dict[str, Any]], **kwargs: Any) -> Base3dPolicyCheck:
        policy_definition = raw_check.get("definition", {})
        check = Base3dPolicyCheck()
        check.iac = policy_definition.get('iac', {})
        check.cve = policy_definition.get('cve', {})
        check.id = raw_check.get("metadata", {}).get("id", "")
        check.name = raw_check.get("metadata", {}).get("name", "")
        check.category = raw_check.get("metadata", {}).get("category", "")
        check.guideline = raw_check.get("metadata", {}).get("guideline")

        return check

    def _parse_check_v1(self, iac_records: list[Record], secrets_records: list[Record], cves_reports: list[ReportCVE]) -> Base3dPolicyCheck:
        check = Base3dPolicyCheck()
        self._fill_check_metadata(check)

        cve_predicaments = [self._create_cve_predicament(cve_report) for cve_report in cves_reports]
        iac_predicaments = [self._create_iac_predicament(iac_record) for iac_record in iac_records]
        secrets_predicaments = [self._create_secrets_predicament(secrets_record) for secrets_record in secrets_records]

        check.predicaments = filter(None, cve_predicaments + iac_predicaments + secrets_predicaments)

        return check



    def _create_cve_predicament(self, cve_report: ReportCVE) -> Predicament | None:
        cve_definition = self.check_definition.get("cves")
        if not cve_definition:
            return None

        if len(cve_definition.keys()) != 1 or any(op in cve_definition.keys() for op in SUPPORTED_LOGICAL_OPERATORS):
            return None

        top_level_logical_op = cve_definition.keys()[0]
        top_level_predicament = Predicament(logical_op=top_level_logical_op)

        nested_definition = cve_definition[top_level_logical_op]
        nested_logical_op = None
        for key, value in nested_definition:
            if key in SUPPORTED_LOGICAL_OPERATORS:
                nested_logical_op = key
            elif key == 'risk_factors':
                top_level_predicament.predicates.append(RiskFactorCVEContains(value, cve_report))

        nested_predicament = None
        if nested_logical_op:
            nested_definition = nested_definition[nested_logical_op]
            if not isinstance(nested_definition, list):
                return None

            nested_predicament = Predicament(logical_op=nested_logical_op)
            for definition in nested_definition:
                for key, value in definition:
                    if key == 'risk_factors':
                        nested_predicament.predicates.append(RiskFactorCVEContains(value, cve_report))

        if nested_predicament:
            top_level_predicament.predicaments.append(nested_predicament)

        return top_level_predicament



    def _create_iac_predicament(self, iac_record: Record) -> Predicament | None:
        pass

    def _create_secrets_predicament(self, secrets_record: Record) -> Predicament | None:
        pass


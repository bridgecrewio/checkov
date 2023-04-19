from __future__ import annotations

import logging
from enum import Enum
from typing import Dict, Any

from checkov.common.util.type_forcers import force_list

from checkov.common.output.record import Record
from checkov.policies_3d.checks_infra.base_parser import Base3dPolicyCheckParser
from checkov.policies_3d.checks_infra.base_check import Base3dPolicyCheck
from checkov.policies_3d.syntax.cves_syntax import RiskFactorCVEContains
from checkov.policies_3d.syntax.iac_syntax import ViolationIdEquals
from checkov.policies_3d.syntax.syntax import Predicament, Predicate
import itertools

SUPPORTED_LOGICAL_OPERATORS = ['and', 'or']
SCA_CHECK_ID_PREFIXES = ['CKV_CVE_', 'BC_LIC_1', 'BC_LIC_2']
SECRETS_CHECK_ID_PREFIXES = ['BC_GIT_']


class PredicateAttributes(str, Enum):
    RISK_FACTOR = 'risk_factor'
    VIOLATION_ID = 'violation_id'


class Policy3dParser(Base3dPolicyCheckParser):
    def __init__(self, raw_check: dict[str, Any] | None = None,
                 resource: str | None = None, records: list[Record] | None = None):
        super().__init__(raw_check)
        self.resource = resource
        self.records = records

    def parse_raw_check(self, raw_check: Dict[str, Dict[str, Any]], **kwargs: Any) -> Base3dPolicyCheck:
        """
        Deprecated. used for the first version of 3D policies
        """
        policy_definition = raw_check.get("definition", {})
        check = Base3dPolicyCheck()
        check.iac = policy_definition.get('iac', {})
        check.cve = policy_definition.get('cve', {})
        check.id = raw_check.get("metadata", {}).get("id", "")
        check.name = raw_check.get("metadata", {}).get("name", "")
        check.category = raw_check.get("metadata", {}).get("category", "")
        check.guideline = raw_check.get("metadata", {}).get("guideline")

        return check

    def _parse_check_v1(self, iac_records: list[Record], secrets_records: list[Record], cves_reports: list[dict[str, Any]]) -> Base3dPolicyCheck:
        check = Base3dPolicyCheck()
        self._fill_check_metadata(check)
        check.predicaments = []

        cves_definition: dict[str, Any] = {}
        iac_definition: dict[str, Any] = {}
        secrets_definition: dict[str, Any] = {}

        for definition in self.check_definition:
            if "cves" in definition.keys():
                cves_definition = definition["cves"]
            elif "iac" in definition.keys():
                iac_definition = definition["iac"]
            elif "secrets" in definition.keys():
                secrets_definition = definition["secrets"]

        cve_predicaments: list[Predicament] = list(filter(None, [self._create_module_predicament(cves_definition, cve_report) for cve_report in cves_reports]))
        iac_predicaments: list[Predicament] = list(filter(None, [self._create_module_predicament(iac_definition, iac_record) for iac_record in iac_records]))
        secrets_predicaments: list[Predicament] = list(filter(None, [self._create_module_predicament(secrets_definition, secrets_record) for secrets_record in secrets_records]))

        # Generating all predicaments combinations while filtering empty lists
        all_combinations = list(itertools.product(*filter(bool, [cve_predicaments, iac_predicaments, secrets_predicaments])))

        for combination in all_combinations:
            check.predicaments.append(
                Predicament(
                    logical_op='and',
                    predicaments=[predicament for predicament in combination]
                )
            )

        return check

    @staticmethod
    def _create_predicate(key: str, value: Any, record: Record | dict[str, Any]) -> Predicate | None:
        if isinstance(record, dict):
            # Specific to cve records passed as dicts
            if key == PredicateAttributes.RISK_FACTOR:
                return RiskFactorCVEContains(force_list(value), record)
        elif isinstance(record, Record):
            if key == PredicateAttributes.VIOLATION_ID:
                return ViolationIdEquals(record, value)

        logging.debug(f"Unable to create predicate for unsupported key {key}")
        return None

    def _create_module_predicament(self, policy_definition: dict[str, Any], record: Record | dict[str, Any]) -> Predicament | None:
        if not policy_definition:
            return None

        top_level_logical_op = ''
        if not any(op in policy_definition.keys() for op in SUPPORTED_LOGICAL_OPERATORS):
            top_level_logical_op = 'and'

        top_level_predicament = Predicament(logical_op=top_level_logical_op)

        for key, value in policy_definition.items():
            if key in SUPPORTED_LOGICAL_OPERATORS:
                top_level_logical_op = key
                top_level_predicament.logical_op = key
            else:
                predicate = self._create_predicate(key, value, record)
                if predicate:
                    top_level_predicament.predicates.append(predicate)

        nested_definition = policy_definition.get(top_level_logical_op)
        if not nested_definition:
            return top_level_predicament

        nested_logical_op = None
        for definition in nested_definition:
            for key, value in definition.items():
                if key in SUPPORTED_LOGICAL_OPERATORS:
                    nested_logical_op = key
                else:
                    predicate = self._create_predicate(key, value, record)
                    if predicate:
                        top_level_predicament.predicates.append(predicate)

        nested_predicament = None
        if nested_logical_op:
            nested_definition = nested_definition[0][nested_logical_op]
            if not isinstance(nested_definition, list):
                return None

            nested_predicament = Predicament(logical_op=nested_logical_op)
            for definition in nested_definition:
                for key, value in definition.items():
                    predicate = self._create_predicate(key, value, record)
                    if predicate:
                        nested_predicament.predicates.append(predicate)

        if nested_predicament:
            top_level_predicament.predicaments.append(nested_predicament)

        return top_level_predicament

from __future__ import annotations

from typing import Dict, Any

from checkov.policies_3d.checks_infra.base_parser import Base3dPolicyCheckParser
from checkov.policies_3d.checks_infra.base_check import Base3dPolicyCheck


class Policy3dParser(Base3dPolicyCheckParser):
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

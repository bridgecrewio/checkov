from typing import List, Dict, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CloudArmorWAFACLCVE202144228(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Cloud Armor prevents message lookup in Log4j2. See CVE-2021-44228 aka log4jshell"
        id = "CKV_GCP_73"
        supported_resources = ("google_compute_security_policy",)
        categories = (CheckCategories.APPLICATION_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        self.evaluated_keys = ["rule"]
        rules = conf.get("rule") or []
        for idx_rule, rule in enumerate(force_list(rules)):
            self.evaluated_keys = [
                f"rule/[{idx_rule}]/action",
                f"rule/[{idx_rule}]/preview",
                f"rule/[{idx_rule}]/match/[0]/expr/[0]/expression",
            ]
            match = rule.get("match")
            if match and isinstance(match, list):
                expr = match[0].get("expr")
                if expr and isinstance(expr[0], dict) and expr[0].get("expression") == ["evaluatePreconfiguredExpr('cve-canary')"]:
                    if rule.get("action") == ["allow"]:
                        return CheckResult.FAILED
                    if rule.get("preview") == [True]:
                        return CheckResult.FAILED

                    return CheckResult.PASSED

        return CheckResult.FAILED


check = CloudArmorWAFACLCVE202144228()

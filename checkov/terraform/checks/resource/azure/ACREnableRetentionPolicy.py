from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ACREnableRetentionPolicy(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure a retention policy is set to cleanup untagged manifests."
        id = "CKV_AZURE_167"
        supported_resources = ("azurerm_container_registry",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if 'retention_policy_in_days' in conf:
            return CheckResult.PASSED

        if 'retention_policy' in conf:
            retention_policy = conf['retention_policy'][0]
            if isinstance(retention_policy, dict) and retention_policy.get('enabled') == [True]:
                return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['retention_policy_in_days', 'retention_policy/enabled']


check = ACREnableRetentionPolicy()

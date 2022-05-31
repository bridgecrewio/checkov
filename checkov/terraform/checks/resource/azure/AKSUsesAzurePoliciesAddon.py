from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AKSUsesAzurePoliciesAddon(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that AKS uses Azure Policies Add-on"
        id = "CKV_AZURE_116"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        # since Azure provider v2.97.0
        azure_policy_enabled = conf.get("azure_policy_enabled", [None])[0]
        if azure_policy_enabled:
            self.evaluated_keys = ["azure_policy_enabled"]
            return CheckResult.PASSED
        # up to and including Azure provider v2.96.0
        self.evaluated_keys = ["addon_profile/[0]/azure_policy/[0]/enabled"]
        addon_profile = conf.get("addon_profile", [None])[0]
        if addon_profile and isinstance(addon_profile, dict):
            azure_policy = addon_profile.get("azure_policy", [None])[0]
            if azure_policy and isinstance(azure_policy, dict) and azure_policy.get("enabled", [None])[0]:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = AKSUsesAzurePoliciesAddon()

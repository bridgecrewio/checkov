from __future__ import annotations

from typing import Dict, List, Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class ACRUseSignedImages(BaseResourceCheck):

    def __init__(self):
        # IN ARM - Set properties.policies.trustPolicy.status to enabled, set
        # properties.policies.trustPolicy.type to Notary
        # This is the default behaviour by the tf provider when the trust policy is enabled
        name = "Ensures that ACR uses signed/trusted images"
        id = "CKV_AZURE_164"
        supported_resources = ("azurerm_container_registry",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if 'trust_policy_enabled' in conf:
            trust_policy_enabled = conf.get('trust_policy_enabled')
            if isinstance(trust_policy_enabled, list) and trust_policy_enabled == [True]:
                return CheckResult.PASSED

        if 'trust_policy' in conf:
            trust_policy = conf['trust_policy'][0]
            if isinstance(trust_policy, dict) and trust_policy.get('enabled') == [True]:
                return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['trust_policy_enabled', 'trust_policy/enabled']


check = ACRUseSignedImages()

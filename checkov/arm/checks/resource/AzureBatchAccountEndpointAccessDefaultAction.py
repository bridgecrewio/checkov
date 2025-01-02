from __future__ import annotations

from typing import Any

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class AzureBatchAccountEndpointAccessDefaultAction(BaseResourceCheck):

    FORBIDDEN_PUBLIC_NETWORK_ACCESS = "enabled"
    FORBIDDEN_NETWORK_ACCESS_DEFAULT_ACTION = "allow"

    def __init__(self) -> None:
        name = "Ensure that Azure Batch account public network access is 'enabled' account access default action is 'ignore'"
        id = "CKV_AZURE_248"
        supported_resources = ("Microsoft.Batch/batchAccounts",)
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    @staticmethod
    def _exists_and_lower_equal(actual_value: Any, expected_lowercase_value: str) -> bool:
        return actual_value and str(actual_value).lower() == expected_lowercase_value

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get('properties')
        if not properties or not isinstance(properties, dict):
            return CheckResult.FAILED

        # public network access is disabled, no need to check for account access default action
        public_network_access = properties.get('publicNetworkAccess')
        if not self._exists_and_lower_equal(public_network_access, self.FORBIDDEN_PUBLIC_NETWORK_ACCESS):
            return CheckResult.PASSED

        network_profile = properties.get('networkProfile')
        if not network_profile:
            return CheckResult.PASSED
        account_access = network_profile.get('accountAccess')
        if not account_access:
            return CheckResult.PASSED
        default_action = account_access.get('defaultAction')
        if not self._exists_and_lower_equal(default_action, self.FORBIDDEN_NETWORK_ACCESS_DEFAULT_ACTION):
            return CheckResult.PASSED

        return CheckResult.FAILED


check = AzureBatchAccountEndpointAccessDefaultAction()

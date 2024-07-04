from typing import Dict, Any, Optional

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class CosmosDBAccountsRestrictedAccess(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Cosmos DB accounts have restricted access"
        id = "CKV_AZURE_99"
        supported_resources = ('Microsoft.DocumentDB/databaseAccounts',)
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        properties: Optional[Dict[str, Any]] = conf.get('properties')
        if properties is not None:
            if 'enableMultipleWriteLocations' not in properties or properties['enableMultipleWriteLocations']:
                self.evaluated_keys = ['enableMultipleWriteLocations']
                if 'isVirtualNetworkFilterEnabled' in properties and properties['isVirtualNetworkFilterEnabled']:
                    self.evaluated_keys.append('isVirtualNetworkFilterEnabled')
                    if 'virtualNetworkRules' in properties and properties['virtualNetworkRules']:
                        self.evaluated_keys.append('virtualNetworkRules')
                        return CheckResult.PASSED
                    if 'ipRules' in properties and properties['ipRules']:
                        self.evaluated_keys.append('ipAddressOrRange')
                        return CheckResult.PASSED
                return CheckResult.FAILED
        return CheckResult.PASSED


check = CosmosDBAccountsRestrictedAccess()

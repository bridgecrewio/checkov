from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class StorageAccountDisablePublicAccess(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Storage accounts disallow public access"
        id = "CKV_AZURE_59"
        supported_resources = ("azurerm_storage_account",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf):
        if 'public_network_access_enabled' in conf:
            self.evaluated_keys = ['public_network_access_enabled']
            if conf['public_network_access_enabled'][0] is False:
                return CheckResult.PASSED
    
        network_conf = [conf]
        evaluated_key_prefix = ''
        if 'network_rules' in conf:
            network_conf = conf['network_rules']
            self.evaluated_keys = ['network_rules']
            evaluated_key_prefix = 'network_rules/[0]/'
        if 'default_action' in network_conf[0]:
            self.evaluated_keys = [f'{evaluated_key_prefix}default_action']
            if network_conf[0]['default_action'][0] == 'Deny':
                return CheckResult.PASSED

        return CheckResult.FAILED


check = StorageAccountDisablePublicAccess()

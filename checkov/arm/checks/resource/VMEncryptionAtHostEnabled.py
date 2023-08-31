from __future__ import annotations

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck

from typing import Any


class VMEncryptionAtHostEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Virtual machine scale sets have encryption at host enabled"
        id = "CKV_AZURE_97"
        supported_resources = ['Microsoft.Compute/virtualMachineScaleSets', 'Microsoft.Compute/virtualMachines']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        securityProfile = None

        if conf.get('properties') and isinstance(conf.get('properties'), dict):
            properties = conf.get('properties')

            if properties.get("virtualMachineProfile") and isinstance(conf.get('properties'), dict):
                profile = properties.get("virtualMachineProfile")
                if profile.get('securityProfile') and isinstance(profile.get('securityProfile'), dict):
                    securityProfile = profile.get('securityProfile')
            if properties.get('securityProfile') and isinstance(properties.get('securityProfile'), dict):
                securityProfile = properties.get('securityProfile')
            if securityProfile is None:
                return CheckResult.FAILED

            if securityProfile.get('encryptionAtHost') and isinstance(securityProfile.get('encryptionAtHost'), str):
                encryptionAtHost = securityProfile.get('encryptionAtHost')
                if encryptionAtHost == "true":
                    return CheckResult.PASSED

        return CheckResult.FAILED


check = VMEncryptionAtHostEnabled()

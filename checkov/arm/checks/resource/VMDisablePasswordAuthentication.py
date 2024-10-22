from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class VMDisablePasswordAuthentication(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Virtual machine does not enable password authentication"
        id = "CKV_AZURE_149"
        supported_resources = (
            "Microsoft.Compute/virtualMachineScaleSets",
            "Microsoft.Compute/virtualMachines",
        )
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        os_profile = None

        properties = conf.get("properties")
        if properties and isinstance(properties, dict):
            if self.entity_type == "Microsoft.Compute/virtualMachines":
                tmp_os_profile = properties.get("osProfile")
                if tmp_os_profile and isinstance(tmp_os_profile, dict):
                    os_profile = tmp_os_profile
            elif self.entity_type == "Microsoft.Compute/virtualMachineScaleSets":
                vm_profile = properties.get("virtualMachineProfile")
                if vm_profile and isinstance(vm_profile, dict):
                    tmp_os_profile = vm_profile.get("osProfile")
                    if tmp_os_profile and isinstance(tmp_os_profile, dict):
                        os_profile = tmp_os_profile

            if os_profile is None:
                return CheckResult.UNKNOWN

            linux_config = os_profile.get("linuxConfiguration")
            if linux_config and isinstance(linux_config, dict):
                pass_auth = linux_config.get("disablePasswordAuthentication")
                if pass_auth and isinstance(pass_auth, bool):
                    return CheckResult.PASSED if pass_auth and isinstance(pass_auth, bool) else CheckResult.FAILED
                return CheckResult.FAILED

            return CheckResult.UNKNOWN

        return CheckResult.FAILED


check = VMDisablePasswordAuthentication()

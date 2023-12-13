from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AzureContainerInstanceEnvVarSecureValueType(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Virtual Machine scale sets Boot Diagnostics are Enabled"
        id = "CKV_AZURE_236"
        supported_resources = ("azurerm_linux_virtual_machine_scale_set", "azurerm_windows_virtual_machine_scale_set",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        boot_diag_blocks = conf.get("boot_diagnostics")
        if boot_diag_blocks is not None:
            for _all_blocks in boot_diag_blocks:
                return CheckResult.PASSED
        else:
            return CheckResult.FAILED


check = AzureContainerInstanceEnvVarSecureValueType()

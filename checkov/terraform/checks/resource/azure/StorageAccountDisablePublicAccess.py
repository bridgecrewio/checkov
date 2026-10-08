from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.type_forcers import force_list
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

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # "public_network_access" (Enabled/Disabled/SecuredByPerimeter) supersedes
        # the deprecated boolean "public_network_access_enabled"
        if "public_network_access" in conf:
            self.evaluated_keys = ["public_network_access"]
            value = force_list(conf["public_network_access"])[0]
            if not isinstance(value, str):
                return CheckResult.FAILED
            if "${" in value:
                return CheckResult.UNKNOWN
            return CheckResult.FAILED if value.lower() == "enabled" else CheckResult.PASSED

        self.evaluated_keys = ["public_network_access_enabled"]
        if "public_network_access_enabled" in conf:
            value = force_list(conf["public_network_access_enabled"])[0]
            if isinstance(value, str) and "${" in value:
                return CheckResult.UNKNOWN
            if value is False or (isinstance(value, str) and value.lower() == "false"):
                return CheckResult.PASSED

        # public network access defaults to enabled
        return CheckResult.FAILED


check = StorageAccountDisablePublicAccess()

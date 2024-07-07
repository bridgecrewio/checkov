from __future__ import annotations

import re
import typing

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


STO_NAME_REGEX = re.compile(r"^[a-z0-9]{3,24}$")
VARIABLE_REFS = ("local.", "module.", "var.", "random_string.", "random_id.", "random_integer.", "random_pet.",
                 "azurecaf_name", "each.")


class StorageAccountName(BaseResourceCheck):
    def __init__(self) -> None:
        """
        Initializes a check to ensure that Storage Accounts adhere to the naming rules.

        The naming reference for Storage Accounts can be found here:
        https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview#naming-storage-accounts
        """
        name = "Ensure Storage Accounts adhere to the naming rules"
        id = "CKV_AZURE_43"
        supported_resources = ['Microsoft.Storage/storageAccounts']
        categories = [CheckCategories.CONVENTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, typing.Any]) -> CheckResult:
        """
        The Storage Account naming reference:
        https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview#naming-storage-accounts
        :param conf: azurerm_storage_account configuration
        :return: <CheckResult>
        """
        if "name" in conf.keys():
            name = conf["name"]
            if name:
                name = str(name)
                if any(x in name for x in VARIABLE_REFS):
                    # in the case we couldn't evaluate the name, just ignore
                    return CheckResult.UNKNOWN
                if re.findall(STO_NAME_REGEX, name):
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = StorageAccountName()

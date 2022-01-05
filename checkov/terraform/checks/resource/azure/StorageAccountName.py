import re
from typing import List, Dict, Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

STO_NAME_REGEX = re.compile(r"^[a-z0-9]{3,24}$")
VARIABLE_REFS = ("local.", "module.", "var.")


class StorageAccountName(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Storage Accounts adhere to the naming rules"
        id = "CKV_AZURE_43"
        supported_resources = ["azurerm_storage_account"]
        categories = [CheckCategories.CONVENTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        """
            The Storage Account naming reference:
            https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview#naming-storage-accounts
        :param conf: azurerm_storage_account configuration
        :return: <CheckResult>
        """
        name = conf.get("name")
        if name:
            name = str(name[0])
            if any(x in name for x in VARIABLE_REFS):
                # in the case we couldn't evaluate the name, just ignore
                return CheckResult.UNKNOWN
            if re.findall(STO_NAME_REGEX, str(conf["name"][0])):
                return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["name"]


check = StorageAccountName()

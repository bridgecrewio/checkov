from typing import List, Dict, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.secrets import string_has_secrets, AZURE, GENERAL
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class VMCredsInCustomData(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that no sensitive credentials are exposed in VM custom_data"
        id = "CKV_AZURE_45"
        supported_resources = ("azurerm_virtual_machine",)
        categories = (CheckCategories.SECRETS,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        os_profile = conf.get("os_profile")
        if os_profile:
            os_profile = os_profile[0]
            if isinstance(os_profile, dict):
                custom_data = os_profile.get("custom_data")
                if custom_data:
                    custom_data = custom_data[0]
                    if isinstance(custom_data, str):
                        if string_has_secrets(custom_data, AZURE, GENERAL):
                            conf[f'{self.id}_secret'] = custom_data
                            return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ["os_profile/[0]/custom_data"]


check = VMCredsInCustomData()

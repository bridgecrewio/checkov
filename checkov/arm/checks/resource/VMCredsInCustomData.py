from typing import List, Dict, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.secrets import string_has_secrets
from checkov.arm.base_resource_value_check import BaseResourceCheck


class VMCredsInCustomData(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that no sensitive credentials are exposed in VM custom_data"
        id = "CKV_AZURE_45"
        supported_resources = ("Microsoft.Compute/virtualMachines",)
        categories = (CheckCategories.SECRETS,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        properties = conf.get("properties")
        if properties and isinstance(properties, dict):
            os_profile = properties.get("osProfile")
            if isinstance(os_profile, dict):
                custom_data = os_profile.get("customData")
                if isinstance(custom_data, str):
                    if string_has_secrets(custom_data):
                        conf[f'{self.id}_secret'] = custom_data
                        return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ["properties/osProfile/customData"]


check = VMCredsInCustomData()

import re
from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.provider.base_check import BaseProviderCheck
from checkov.common.models.consts import panos_api_key_pattern


class PanosCredentials(BaseProviderCheck):
    def __init__(self) -> None:
        name = "Ensure no hard coded PAN-OS credentials exist in provider"
        id = "CKV_PAN_1"
        supported_provider = ["panos"]
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_provider=supported_provider)

    def scan_provider_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        result = CheckResult.PASSED
        if self.secret_found(conf, "api_key", panos_api_key_pattern):
            result = CheckResult.FAILED

        password = conf.get("password")
        if password:
            conf[f'{self.id}_secret_pwd'] = password
            result = CheckResult.FAILED
        return result

    def secret_found(self, conf: Dict[str, List[Any]], field: str, pattern: str) -> bool:
        if field in conf.keys():
            value = conf[field][0]
            if not isinstance(value, str) or re.match(pattern, value) is not None:
                if isinstance(value, str):
                    conf[f'{self.id}_secret'] = value
                return True
        return False


check = PanosCredentials()

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
        if self.secret_found(conf, "api_key", panos_api_key_pattern):
            return CheckResult.FAILED
        if conf.get("password"):
            return CheckResult.FAILED
        return CheckResult.PASSED

    @staticmethod
    def secret_found(conf: Dict[str, List[Any]], field: str, pattern: str) -> bool:
        if field in conf.keys():
            value = conf[field][0]
            if re.match(pattern, value) is not None:
                return True
        return False


check = PanosCredentials()

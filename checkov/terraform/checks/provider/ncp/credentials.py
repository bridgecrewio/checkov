import re
from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.provider.base_check import BaseProviderCheck
from checkov.common.models.consts import access_key_pattern, secret_key_pattern


class NCPCredentials(BaseProviderCheck):
    def __init__(self) -> None:
        name = "Ensure no hard coded NCP access key and secret key exists in provider"
        id = "CKV_NCP_17"
        supported_provider = ("ncloud",)
        categories = (CheckCategories.SECRETS,)
        super().__init__(name=name, id=id, categories=categories, supported_provider=supported_provider)

    def scan_provider_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """
        see: https://registry.terraform.io/providers/NaverCloudPlatform/ncloud/latest/docs
        """
        result = CheckResult.PASSED
        if self.secret_found(conf, "access_key", access_key_pattern):
            result = CheckResult.FAILED
        if self.secret_found(conf, "secret_key", secret_key_pattern):
            result = CheckResult.FAILED
        return result

    def secret_found(self, conf: Dict[str, List[Any]], field: str, pattern: str) -> bool:
        if field in conf.keys():
            value = conf[field][0]
            if isinstance(value, str) and re.match(pattern, value) is not None:
                conf[f'{self.id}_secret_{field}'] = value
                return True
        return False


check = NCPCredentials()

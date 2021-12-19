from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.provider.base_check import BaseProviderCheck


class OciCredentials(BaseProviderCheck):
    def __init__(self) -> None:
        name = "Ensure no hard coded OCI private key in provider"
        id = "CKV_OCI_1"
        supported_provider = ["oci"]
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_provider=supported_provider)

    def scan_provider_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        key = "private_key_password"
        if key in conf.keys():
            if not conf[key]:
                return CheckResult.PASSED
            return CheckResult.FAILED
        else:
            return CheckResult.PASSED


check = OciCredentials()

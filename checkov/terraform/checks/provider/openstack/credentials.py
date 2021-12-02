from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.provider.base_check import BaseProviderCheck


class OpenstackCredentials(BaseProviderCheck):
    def __init__(self) -> None:
        name = "Ensure no hard coded OpenStack password, token, or application_credential_secret exists in provider"
        id = "CKV_OPENSTACK_1"
        supported_provider = ["openstack"]
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_provider=supported_provider)

    def scan_provider_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """
        see: https://registry.terraform.io/providers/terraform-provider-openstack/openstack/latest/docs#configuration-reference
        """
        if conf.get("password"):
            return CheckResult.FAILED
        if conf.get("token"):
            return CheckResult.FAILED
        if conf.get("application_credential_secret"):
            return CheckResult.FAILED
        return CheckResult.PASSED


check = OpenstackCredentials()

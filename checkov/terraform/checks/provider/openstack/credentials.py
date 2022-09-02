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
        result = CheckResult.PASSED
        if conf.get("password"):
            conf[f'{self.id}_secret_1'] = conf.get('password')[0]
            result = CheckResult.FAILED
        if conf.get("token"):
            conf[f'{self.id}_secret_2'] = conf.get('token')[0]
            result = CheckResult.FAILED
        if conf.get("application_credential_secret"):
            conf[f'{self.id}_secret_3'] = conf.get('application_credential_secret')[0]
            result = CheckResult.FAILED
        return result


check = OpenstackCredentials()

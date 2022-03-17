from typing import List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class APIManagementCertsEnforced(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Client Certificates are enforced for API management"
        id = "CKV_AZURE_152"
        supported_resources = ['azurerm_api_management']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('sku_name'):
            if conf['sku_name'] == ["Consumption"]:
                if conf.get('client_certificate_enabled'):
                    if conf.get('client_certificate_enabled') == [True]:
                        return CheckResult.PASSED
                self.evaluated_keys = ['/client_certificate_enabled/']
                return CheckResult.FAILED
        return CheckResult.UNKNOWN


check = APIManagementCertsEnforced()

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ACRAnonymousPullDisabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensures that ACR disables anonymous pulling of images"
        id = "CKV_AZURE_138"
        supported_resources = ['azurerm_container_registry']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # anonymous_pull_enabled only applies to Standard and Premium skus, by default is set to false
        if ('sku' in conf.keys() and conf['sku'][0] in ["Standard", "Premium"] 
            and 'anonymous_pull_enabled' in conf.keys() and conf['anonymous_pull_enabled'][0]):
            return CheckResult.FAILED

        return CheckResult.PASSED


check = ACRAnonymousPullDisabled()

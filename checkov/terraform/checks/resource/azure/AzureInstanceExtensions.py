from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AzureInstanceExtensions(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Virtual Machine Extensions are not Installed"
        id = "CKV_AZURE_50"
        supported_resources = ['azurerm_virtual_machine', 'azurerm_linux_virtual_machine']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Virtual Machine Extensions Installed at azure_instance:
            https://www.terraform.io/docs/providers/azure/r/instance.html
        :param conf: azure_instance configuration
        :return: <CheckResult>
        """
        if 'allow_extension_operations' in conf.keys():
            config = conf['allow_extension_operations'][0]
            if config:
                return CheckResult.FAILED
            else:
                return CheckResult.PASSED 
        return CheckResult.PASSED


check = AzureInstanceExtensions()

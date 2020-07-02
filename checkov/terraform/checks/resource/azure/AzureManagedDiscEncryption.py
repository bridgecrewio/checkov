from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AzureManagedDiscEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Azure managed disk have encryption enabled"
        id = "CKV_AZURE_2"
        supported_resources = ['azurerm_managed_disk']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at azure_instance:
            https://www.terraform.io/docs/providers/azure/r/instance.html
        :param conf: azure_instance configuration
        :return: <CheckResult>
        """
        if 'encryption_settings' in conf.keys():
            config = conf['encryption_settings'][0]
            if isinstance(config, dict) and not config['enabled'][0]:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = AzureManagedDiscEncryption()

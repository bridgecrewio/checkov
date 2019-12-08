from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class AzureManagedDiscEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Azure managed disk have encryption enabled"
        id = "BC_AZURE_DISC_1"
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
            if config['enabled'] ==[False]:
                return CheckResult.FAILURE
        return CheckResult.SUCCESS


check = AzureManagedDiscEncryption()

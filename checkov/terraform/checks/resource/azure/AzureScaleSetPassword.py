from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AzureScaleSetPassword(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Azure linux scale set does not use basic authentication(Use SSH Key Instead)"
        id = "CKV_AZURE_48"
        supported_resources = ['azurerm_linux_virtual_machine_scale_set']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at azure_instance:
            https://www.terraform.io/docs/providers/azurerm/r/linux_virtual_machine_scale_set.html
        :param conf: azurerm_linux_virtual_machine_scale_set configuration
        :return: <CheckResult>
        """
        if 'disable_password_authentication' in conf.keys():
            if conf.get('disable_password_authentication', [True])[0]:
                return CheckResult.PASSED

        return CheckResult.FAILED


check = AzureScaleSetPassword()

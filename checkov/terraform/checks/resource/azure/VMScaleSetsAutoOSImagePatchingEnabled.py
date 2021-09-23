from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class VMScaleSetsAutoOSImagePatchingEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that automatic OS image patching is enabled for Virtual Machine Scale Sets"
        id = "CKV_AZURE_95"
        supported_resources = ['azurerm_virtual_machine_scale_set']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'automatic_os_upgrade' in conf and conf['automatic_os_upgrade'][0] \
                and 'os_profile_windows_config' in conf and conf['os_profile_windows_config'][0]:
            os_profile_windows_config = conf['os_profile_windows_config'][0]
            self.evaluated_keys = ['os_profile_windows_config']
            if 'enable_automatic_upgrades' in os_profile_windows_config \
                    and os_profile_windows_config['enable_automatic_upgrades'][0]:
                self.evaluated_keys = ['automatic_os_upgrade',
                                       'os_profile_windows_config/[0]/enable_automatic_upgrades']
                return CheckResult.PASSED
        return CheckResult.FAILED


check = VMScaleSetsAutoOSImagePatchingEnabled()

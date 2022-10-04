
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class LaunchConfigurationEncryptionVPC(BaseResourceCheck):
    def __init__(self):
        name = "You can set whether to encrypt basic block storage if server image is RHV. Default false." \
               " Only support VPC environment."
        id = "CKV_NCP_4"
        supported_resources = ['ncloud_launch_configuration']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'is_encrypted_volume' in conf.keys():
            is_encrypted_volume = conf['is_encrypted_volume']
            if is_encrypted_volume == [True]:
                return CheckResult.PASSED
            else:
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED


check = LaunchConfigurationEncryptionVPC()
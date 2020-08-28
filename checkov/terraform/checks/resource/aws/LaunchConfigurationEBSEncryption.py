from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class LaunchConfigurationEBSEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the Launch configuration EBS is securely encrypted"
        id = "CKV_AWS_8"
        supported_resources = ['aws_launch_configuration', 'aws_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "*_block_device/[0]/encrypted"

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at launch configuration:
            https://www.terraform.io/docs/providers/aws/r/launch_configuration.html or https://www.terraform.io/docs/providers/aws/d/instance.html
        :param conf: aws_launch_configuration configuration
        :return: <CheckResult>
        """
        have_root_block = 0
        for key in conf.keys():
            if "block_device" in key and "ephemeral" not in key:
                if isinstance(conf[key][0], dict) and conf[key][0].get("encrypted") != [True]:
                    return CheckResult.FAILED
            if "root_block_device" in key:
                # Issue 496 - TF will create unencrypted EBS root by default if whole root_block_device block is omitted.
                have_root_block = 1
        if have_root_block == 0: 
            return CheckResult.FAILED

        return CheckResult.PASSED


check = LaunchConfigurationEBSEncryption()

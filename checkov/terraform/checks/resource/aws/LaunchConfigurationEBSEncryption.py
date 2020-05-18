from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class LaunchConfigurationEBSEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the Launch configuration EBS is securely encrypted "
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
        for key in conf.keys():
            if "block_device" in key and "ephemeral" not in key:
                if "encrypted" in conf[key][0]:
                    if conf[key][0]["encrypted"] == [False]:
                        return CheckResult.FAILED
                    else:
                        return CheckResult.PASSED
                else:
                    return CheckResult.FAILED
        return CheckResult.FAILED


check = LaunchConfigurationEBSEncryption()

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class LaunchConfigurationEBSEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the Launch configuration EBS is securely encrypted"
        id = "CKV_AWS_8"
        supported_resources = ['AWS::AutoScaling::LaunchConfiguration']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        Looks for encryption configuration of device block mapping in an AWS launch configurations
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-launchconfig-blockdev-template.html
        :param conf: aws_launch_configuration configuration
        :return: <CheckResult>
        """
        properties = conf.get('Properties', {})
        if properties is None:
            return CheckResult.UNKNOWN
        block_device_mappings = properties.get('BlockDeviceMappings')
        if block_device_mappings is None:
            return CheckResult.UNKNOWN
        if not isinstance(block_device_mappings, list):
            return CheckResult.UNKNOWN
        for block_device_mapping in block_device_mappings:
            if not isinstance(block_device_mapping, dict):
                return CheckResult.UNKNOWN
            if block_device_mapping.get('Ebs'):
                if not block_device_mapping['Ebs'].get('Encrypted'):
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = LaunchConfigurationEBSEncryption()

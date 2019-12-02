from checkov.terraformscanner.models.enums import ScanResult, ScanCategories
from checkov.terraformscanner.resource_scanner import ResourceScanner


class LaunchConfigurationEBSEncryption(ResourceScanner):
    def __init__(self):
        name = "Ensure all data stored in the Launch configuration EBS is securely encrypted "
        scan_id = "BC_AWS_EBS_1"
        supported_resources = ['aws_launch_configuration','aws_instance']
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at launch configuration:
            https://www.terraform.io/docs/providers/aws/r/launch_configuration.html or https://www.terraform.io/docs/providers/aws/d/instance.html
        :param conf: aws_launch_configuration configuration
        :return: <ScanResult>
        """
        for key in conf.keys():
            if "block_device" in key and "ephemeral" not in key:
                if "encrypted" in conf[key][0]:
                    if conf[key][0]["encrypted"] == [False]:
                        return ScanResult.FAILURE
                    else:
                        return ScanResult.SUCCESS
                else:
                    return ScanResult.FAILURE
        return ScanResult.SUCCESS


scanner = LaunchConfigurationEBSEncryption()

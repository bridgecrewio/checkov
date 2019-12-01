from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.resource_scanner import ResourceScanner


class EBSEncryption(ResourceScanner):
    def __init__(self):
        name = "Ensure all data stored in the EBS is securely encrypted "
        scan_id = "BC_AWS_EBS_2"
        supported_resources = ['aws_ebs_volume']
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at ebs volume:
            https://www.terraform.io/docs/providers/aws/r/ebs_volume.html
        :param conf: ebs_volume configuration
        :return: <ScanResult>
        """
        if "encrypted" in conf.keys():
            if conf["encrypted"][0] == True:
                return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = EBSEncryption()

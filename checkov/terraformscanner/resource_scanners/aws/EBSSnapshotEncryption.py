from checkov.terraformscanner.models.enums import ScanResult, ScanCategories
from checkov.terraformscanner.resource_scanner import ResourceScanner


class EBSSnapshotEncryption(ResourceScanner):
    def __init__(self):
        name = "Ensure all data stored in the EBS Snapshot is securely encrypted "
        scan_id = "BC_AWS_EBS_4"
        supported_resources = ['aws_ebs_snapshot']
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at EBS snapshot:
            https://www.terraform.io/docs/providers/aws/r/ebs_snapshot.html
        :param conf: aws_ebs_snapshot configuration
        :return: <ScanResult>
        """
        if "encrypted" in conf.keys():
            if conf["encrypted"][0] == True:
                return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = EBSSnapshotEncryption()

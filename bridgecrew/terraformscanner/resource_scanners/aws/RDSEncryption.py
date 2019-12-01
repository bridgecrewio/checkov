from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.resource_scanner import ResourceScanner


class RDSEncryption(ResourceScanner):
    def __init__(self):
        name = "Ensure all data stored in the RDS bucket is securely encrypted at rest"
        scan_id = "BC_AWS_RDS_1"
        supported_resources = ['aws_db_instance']
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_db_instance:
            https://www.terraform.io/docs/providers/aws/d/db_instance.html
        :param conf: aws_db_instance configuration
        :return: <ScanResult>
        """
        if 'storage_encrypted' in conf.keys():
            key = conf['storage_encrypted'][0]
            if key:
                return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = RDSEncryption()

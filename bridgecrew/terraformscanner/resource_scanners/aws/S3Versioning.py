from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.resource_scanner import ResourceScanner


class S3VersioningScanner(ResourceScanner):
    def __init__(self):
        name = "Ensure all data stored in the S3 bucket is securely encrypted at rest"
        scan_id = "BC_AWS_S3_16"
        supported_resources = ['aws_s3_bucket']
        categories = [ScanCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for logging configuration at aws_s3_bucket:
            https://www.terraform.io/docs/providers/aws/r/s3_bucket.html
        :param conf: aws_s3_bucket configuration
        :return: <ScanResult>
        """
        if 'versioning' in conf.keys():
            versioning_block = conf['versioning'][0]
            if versioning_block['enabled'][0]:
                return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = S3VersioningScanner()

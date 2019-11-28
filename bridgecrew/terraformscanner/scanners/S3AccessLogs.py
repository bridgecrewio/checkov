from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.scanner import Scanner


class S3AccessLogsScanner(Scanner):
    def __init__(self):
        name = "Ensure the S3 bucket has access logging enabled"
        scan_id = "BC_AWS_S3_13"
        supported_resource = 'aws_s3_bucket'
        categories = [ScanCategories.LOGGING]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resource=supported_resource)

    def scan_resource_conf(self, conf):
        """
            Looks for logging configuration at aws_s3_bucket:
            https://www.terraform.io/docs/providers/aws/r/s3_bucket.html
        :param conf: aws_s3_bucket configuration
        :return: <ScanResult>
        """
        if 'logging' in conf.keys():
            return ScanResult.SUCCESS
        else:
            return ScanResult.FAILURE


scanner = S3AccessLogsScanner()

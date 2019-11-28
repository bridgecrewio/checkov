from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.scanner import Scanner


class S3EncryptionScanner(Scanner):
    def __init__(self):
        name = "Ensure all data stored in the S3 bucket is securely encrypted at rest"
        scan_id = "BC_AWS_S3_14"
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
        if 'server_side_encryption_configuration' in conf.keys():
            sse_block = conf['server_side_encryption_configuration']
            if 'rule' in sse_block.keys():
                rule_block = sse_block['rule']
                if 'apply_server_side_encryption_by_default' in rule_block.keys() and 'sse_algorithm' in rule_block.keys():
                    return ScanResult.SUCCESS
            return ScanResult.FAILURE


scanner = S3EncryptionScanner()

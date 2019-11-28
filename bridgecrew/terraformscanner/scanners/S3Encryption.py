from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.scanner import Scanner


class S3EncryptionScanner(Scanner):
    def __init__(self):
        name = "Ensure all data stored in the S3 bucket is securely encrypted at rest"
        scan_id = "BC_AWS_S3_14"
        supported_resource = 'aws_s3_bucket'
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resource=supported_resource)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_s3_bucket:
            https://www.terraform.io/docs/providers/aws/r/s3_bucket.html
        :param conf: aws_s3_bucket configuration
        :return: <ScanResult>
        """
        if 'server_side_encryption_configuration' in conf.keys():
            sse_block = conf['server_side_encryption_configuration']
            if 'rule' in sse_block[0].keys():
                rule_block = sse_block[0]['rule']
                if 'apply_server_side_encryption_by_default' in rule_block[0].keys():
                    encryption_block = rule_block[0]['apply_server_side_encryption_by_default']
                    if  'sse_algorithm' in encryption_block[0].keys():
                        return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = S3EncryptionScanner()

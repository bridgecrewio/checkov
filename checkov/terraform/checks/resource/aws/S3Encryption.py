from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class S3Encryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the S3 bucket is securely encrypted at rest"
        id = "CKV_AWS_19"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_s3_bucket:
            https://www.terraform.io/docs/providers/aws/r/s3_bucket.html
        :param conf: aws_s3_bucket configuration
        :return: <CheckResult>
        """
        if 'server_side_encryption_configuration' in conf.keys():
            sse_block = conf['server_side_encryption_configuration']
            if 'rule' in sse_block[0].keys():
                rule_block = sse_block[0]['rule']
                if 'apply_server_side_encryption_by_default' in rule_block[0].keys():
                    encryption_block = rule_block[0]['apply_server_side_encryption_by_default']
                    if  'sse_algorithm' in encryption_block[0].keys():
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = S3Encryption()

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SQSQueueEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the SQS queue  is encrypted"
        id = "CKV_AWS_27"
        supported_resources = ['aws_sqs_queue']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_sqs_queue:
            https://www.terraform.io/docs/providers/aws/r/sqs_queue.html
        :param conf: aws_s3_bucket configuration
        :return: <CheckResult>
        """
        if 'kms_master_key_id' in conf.keys():
            if conf['kms_master_key_id']:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = SQSQueueEncryption()

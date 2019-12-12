from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class SNSTopicEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the SNS topic is encrypted"
        id = "CKV_AWS_26"
        supported_resources = ['aws_sns_topic']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_sns_topic:
            https://www.terraform.io/docs/providers/aws/r/sns_topic.html
        :param conf: aws_s3_bucket configuration
        :return: <CheckResult>
        """
        if 'kms_master_key_id' in conf.keys():
            if conf['kms_master_key_id']:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = SNSTopicEncryption()

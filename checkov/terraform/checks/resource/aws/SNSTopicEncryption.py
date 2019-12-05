from checkov.terraform.models.enums import ScanResult, ScanCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class SNSTopicEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the SNS topic is encrypted"
        scan_id = "BC_AWS_SNS_1"
        supported_resources = ['aws_sns_topic']
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_sns_topic:
            https://www.terraform.io/docs/providers/aws/r/sns_topic.html
        :param conf: aws_s3_bucket configuration
        :return: <ScanResult>
        """
        if 'kms_master_key_id' in conf.keys():
            if conf['kms_master_key_id']:
                return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = SNSTopicEncryption()

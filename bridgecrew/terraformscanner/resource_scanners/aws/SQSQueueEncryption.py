from bridgecrew.terraformscanner.models.enums import ScanResult, ScanCategories
from bridgecrew.terraformscanner.resource_scanner import ResourceScanner


class SQSQueueEncryption(ResourceScanner):
    def __init__(self):
        name = "Ensure all data stored in the SQS queue bucket is encrypted"
        scan_id = "BC_AWS_SQS_1"
        supported_resources = ['aws_sqs_queue']
        categories = [ScanCategories.ENCRYPTION]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for encryption configuration at aws_sqs_queue:
            https://www.terraform.io/docs/providers/aws/r/sqs_queue.html
        :param conf: aws_s3_bucket configuration
        :return: <ScanResult>
        """
        if 'kms_master_key_id' in conf.keys():
            if conf['kms_master_key_id']:
                return ScanResult.SUCCESS
        return ScanResult.FAILURE


scanner = SQSQueueEncryption()

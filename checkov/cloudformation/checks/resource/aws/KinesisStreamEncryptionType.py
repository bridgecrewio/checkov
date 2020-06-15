from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class KinesisStreamEncryptionType(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Kinesis Stream is securely encrypted"
        id = "CKV_AWS_43"
        supported_resources = ['AWS::Kinesis::Stream']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        Looks for KMS encryption of a Kinesis stream
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesis-stream.html#cfn-kinesis-stream-streamencryption
        :param conf: aws_kinesis_stream
        :return: <CheckResult>
        """
        if 'Properties' in conf.keys():
            if 'StreamEncryption' in conf['Properties'].keys():
                if 'EncryptionType' in conf['Properties']['StreamEncryption']:
                    encryption_type = conf['Properties']['StreamEncryption']['EncryptionType']
                    if encryption_type == 'KMS':
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = KinesisStreamEncryptionType()

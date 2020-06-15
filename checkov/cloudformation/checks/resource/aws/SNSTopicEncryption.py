from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class SNSTopicEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the SNS topic is encrypted"
        id = "CKV_AWS_26"
        supported_resources = ['AWS::SNS::Topic']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('Properties'):
            if conf['Properties'].get('KmsMasterKeyId'):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = SNSTopicEncryption()

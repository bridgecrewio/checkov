from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

class AmazonMQBrokerPublicAccess(BaseResourceCheck):

    def __init__(self):
        name = "Ensure Amazon MQ Broker should not have public access"
        id = "CKV_AWS_166"
        supported_resources = ['AWS::AmazonMQ::Broker']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            validates Amazon MQ Broker should not have public access
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html
        :return: <CheckResult>
        """

        if 'Properties' in conf.keys():
            if 'PubliclyAccessible' in conf['Properties'].keys():
                if conf['Properties']['PubliclyAccessible'] is True:
                    return CheckResult.FAILED
                else:
                    return CheckResult.PASSED
        return CheckResult.PASSED

check = AmazonMQBrokerPublicAccess()

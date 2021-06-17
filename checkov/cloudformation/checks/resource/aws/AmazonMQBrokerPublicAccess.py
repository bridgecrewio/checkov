from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck

class AmazonMQBrokerPublicAccess(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure Amazon MQ Broker should not have public access"
        id = "CKV_AWS_69"
        supported_resources = ['AWS::AmazonMQ::Broker']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, missing_block_result=CheckResult.FAILED)

    def get_expected_value(self):
        return False

    def get_inspected_key(self):
        """
            validates Amazon MQ Broker should not have public access
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html
        :return: <CheckResult>
        """
        return 'Properties/PubliclyAccessible'


check = AmazonMQBrokerPublicAccess()

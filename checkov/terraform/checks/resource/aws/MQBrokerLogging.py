from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class MQBrokerLogging(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure MQ Broker logging is enabled"
        id = "CKV_AWS_48"
        supported_resources = ['aws_mq_broker']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "logs/[0]/general"


check = MQBrokerLogging()

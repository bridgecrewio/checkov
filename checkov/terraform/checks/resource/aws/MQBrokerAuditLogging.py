from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories,CheckResult


class MQBrokerAuditLogging(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure MQ Broker Audit logging is enabled"
        id = "CKV_AWS_197"
        supported_resources = ['aws_mq_broker']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/security-logging-monitoring-rabbitmq.html
        # Audit logging is not supported for RabbitMQ brokers.
        if conf.get("engine_type") == ["RabbitMQ"]:
            return CheckResult.UNKNOWN
        return super().scan_resource_conf(conf)

    def get_inspected_key(self):
        return "logs/[0]/audit"


check = MQBrokerAuditLogging()

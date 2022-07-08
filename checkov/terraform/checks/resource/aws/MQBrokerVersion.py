import re

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

minimumActiveMQ = 5.16
minimumRabbitMQ = 3.8


class MQBrokerVersion(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure MQBroker version is current"
        id = "CKV_AWS_208"
        supported_resources = ("aws_mq_broker", "aws_mq_configuration")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("engine_type"):
            mq_type = conf.get("engine_type")[0]
            semantic = conf.get("engine_version", [''])[0]
            if not re.search(r'(\d+\.\d+.\d+)', semantic):
                return CheckResult.UNKNOWN
            version = float(re.search(r'(\d+\.\d+)', semantic).group())
            if mq_type in 'ActiveMQ':
                if version >= minimumActiveMQ:
                    return CheckResult.PASSED

            if mq_type in 'RabbitMQ':
                if version >= minimumRabbitMQ:
                    return CheckResult.PASSED

        return CheckResult.FAILED


check = MQBrokerVersion()

import re
from typing import List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

ENGINE_VERSION_PATTERN = re.compile(r"(\d+\.\d+.\d+)")
ENGINE_VERSION_SHORT_PATTERN = re.compile(r"(\d+\.\d+)")
MINIMUM_ACTIVEMQ_VERSION = 5.17
MINIMUM_RABBITMQ_VERSION = 3.11


class MQBrokerVersion(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure MQ Broker version is current"
        id = "CKV_AWS_208"
        supported_resources = ("aws_mq_broker", "aws_mq_configuration")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    @staticmethod
    def version_string_to_tuple(version_str) -> tuple:
        return tuple(map(int, str(version_str).split('.')))

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("engine_type"):
            mq_type = conf.get("engine_type")[0]
            semantic = conf.get("engine_version", [''])[0]
            if not re.search(ENGINE_VERSION_PATTERN, semantic):
                return CheckResult.UNKNOWN
            version_tuple = self.version_string_to_tuple(re.search(ENGINE_VERSION_SHORT_PATTERN, semantic).group())
            if mq_type in 'ActiveMQ':
                if version_tuple >= self.version_string_to_tuple(MINIMUM_ACTIVEMQ_VERSION):
                    return CheckResult.PASSED

            if mq_type in 'RabbitMQ':
                if version_tuple >= self.version_string_to_tuple(MINIMUM_RABBITMQ_VERSION):
                    return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["engine_type", "engine_version"]


check = MQBrokerVersion()

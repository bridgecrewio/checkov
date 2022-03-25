from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class MQBrokerNotPubliclyExposed(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure MQ Broker is not publicly exposed"
        id = "CKV_AWS_69"
        supported_resources = ("aws_mq_broker",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        """
        Looks for public accessibility:
            https://www.terraform.io/docs/providers/aws/r/mq_broker.html#publicly_accessible
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-amazonmq-broker.html
        :param conf: aws_launch_configuration configuration
        :return: <CheckResult>
        """
        return "publicly_accessible"

    def get_forbidden_values(self) -> list[Any]:
        return [True]


check = MQBrokerNotPubliclyExposed()

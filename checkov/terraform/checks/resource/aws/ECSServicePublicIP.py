from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from typing import Any, List


class ECSServicePublicIP(BaseResourceNegativeValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 AC-21, NIST.800-53.r5 AC-3, NIST.800-53.r5 AC-3(7), NIST.800-53.r5 AC-4, NIST.800-53.r5 AC-4(21),
        NIST.800-53.r5 AC-6, NIST.800-53.r5 SC-7, NIST.800-53.r5 SC-7(11), NIST.800-53.r5 SC-7(16),
        NIST.800-53.r5 SC-7(20), NIST.800-53.r5 SC-7(21), NIST.800-53.r5 SC-7(3), NIST.800-53.r5 SC-7(4),
        NIST.800-53.r5 SC-7(9)
        ECS services should not have public IP addresses assigned to them automatically
        """
        name = "Ensure ECS services do not have public IP addresses assigned to them automatically"
        id = "CKV_AWS_333"
        supported_resources = ["aws_ecs_service"]
        categories = [CheckCategories.LOGGING]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "network_configuration/[0]/assign_public_ip"

    def get_forbidden_values(self) -> List[Any]:
        return [True]


check = ECSServicePublicIP()

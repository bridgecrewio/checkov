from __future__ import annotations

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from typing import Any


class LambdaFunctionIsNotPublic(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        """
        PCI DSS v3.2.1/1.2.1, PCI DSS v3.2.1/1.3.1, PCI DSS v3.2.1/1.3.2, PCI DSS v3.2.1/1.3.4, PCI DSS v3.2.1/7.2.1,
        NIST.800-53.r5 AC-21, NIST.800-53.r5 AC-3, NIST.800-53.r5 AC-3(7), NIST.800-53.r5 AC-4, NIST.800-53.r5 AC-4(21),
        NIST.800-53.r5 AC-6, NIST.800-53.r5 SC-7, NIST.800-53.r5 SC-7(11), NIST.800-53.r5 SC-7(16), NIST.800-53.r5 SC-7(20),
        NIST.800-53.r5 SC-7(21), NIST.800-53.r5 SC-7(3), NIST.800-53.r5 SC-7(4), NIST.800-53.r5 SC-7(9)
        Lambda function policies should prohibit public access
        """

        name = "Ensure that AWS Lambda function is not publicly accessible"
        id = "CKV_AWS_301"
        supported_resources = ("aws_lambda_permission",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "principal"

    def get_forbidden_values(self) -> list[Any]:
        return ["*"]


check = LambdaFunctionIsNotPublic()

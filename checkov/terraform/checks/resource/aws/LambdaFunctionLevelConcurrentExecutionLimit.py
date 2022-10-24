from __future__ import annotations

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from typing import Any


class LambdaFunctionLevelConcurrentExecutionLimit(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that AWS Lambda function is configured for function-level concurrent execution limit"
        id = "CKV_AWS_115"
        supported_resources = ("aws_lambda_function",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_attribute_result=CheckResult.FAILED,
        )

    def get_inspected_key(self) -> str:
        return "reserved_concurrent_executions/[0]"

    def get_forbidden_values(self) -> list[Any]:
        return ["${-1}"]


check = LambdaFunctionLevelConcurrentExecutionLimit()

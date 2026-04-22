from __future__ import annotations

from typing import Any
from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class LambdaCodeSigningConfigured(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure AWS Lambda function is configured to validate code-signing"
        id = "CKV_AWS_272"
        supported_resources = ['aws_lambda_function']
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any], entity_type: str = None):
        # Code signing only applies to Zip package type, not Image (container)
        if conf.get("package_type") == "Image":
            return CheckResult.PASSED
        return super().scan_resource_conf(conf, entity_type)

    def get_inspected_key(self):
        return "code_signing_config_arn"

    def get_expected_value(self):
        return ANY_VALUE


check = LambdaCodeSigningConfigured()

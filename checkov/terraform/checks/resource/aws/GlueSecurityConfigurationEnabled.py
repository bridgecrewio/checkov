from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GlueSecurityConfigurationEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Glue component has a security configuration associated"
        id = "CKV_AWS_195"
        supported_resources = ("aws_glue_crawler", "aws_glue_dev_endpoint", "aws_glue_job")
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "security_configuration"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = GlueSecurityConfigurationEnabled()

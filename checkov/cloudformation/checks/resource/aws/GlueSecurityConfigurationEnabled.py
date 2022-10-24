from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GlueSecurityConfigurationEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Glue component has a security configuration associated"
        id = "CKV_AWS_195"
        supported_resources = ("AWS::Glue::Crawler", "AWS::Glue::DevEndpoint", "AWS::Glue::Job")
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        if self.entity_type == "AWS::Glue::Crawler":
            return "Properties/CrawlerSecurityConfiguration"
        elif self.entity_type in ("AWS::Glue::DevEndpoint", "AWS::Glue::Job"):
            return "Properties/SecurityConfiguration"

        return ""

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = GlueSecurityConfigurationEnabled()

from __future__ import annotations

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CDNEnableHttpsEndpoints(BaseResourceValueCheck):
    def __init__(self) -> None:
        # This is the full description of your check
        description = "Ensure the Azure CDN enables the HTTPS endpoint"

        # This is the Unique ID for your check
        id = "CKV_AZURE_198"

        # These are the Terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ("azurerm_cdn_endpoint",)

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = (CheckCategories.NETWORKING,)
        super().__init__(
            name=description,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.PASSED,
        )

    def get_inspected_key(self) -> str:
        return "is_https_allowed"


check = CDNEnableHttpsEndpoints()

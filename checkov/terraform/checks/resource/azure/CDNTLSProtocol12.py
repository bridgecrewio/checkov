from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

INSECURE_TLS_VERSIONS = ("None", "TLS10")


class CDNTLSProtocol12(BaseResourceCheck):
    def __init__(self) -> None:
        # This is the full description of your check
        description = "Ensure the Azure CDN endpoint is using the latest version of TLS encryption"

        # This is the Unique ID for your check
        id = "CKV_AZURE_200"

        # These are the Terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ("azurerm_cdn_endpoint_custom_domain",)

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if "cdn_managed_https" in conf and isinstance(conf["cdn_managed_https"], list):
            cdn = conf["cdn_managed_https"][0]
            if "tls_version" in cdn and isinstance(cdn["tls_version"], list) and cdn["tls_version"][0] in INSECURE_TLS_VERSIONS:
                return CheckResult.FAILED
        if "user_managed_https" in conf and isinstance(conf["user_managed_https"], list):
            user = conf["user_managed_https"][0]
            if "tls_version" in user and isinstance(user["tls_version"], list) and user["tls_version"][0] in INSECURE_TLS_VERSIONS:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = CDNTLSProtocol12()

from __future__ import annotations

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CDNTLSProtocol12(BaseResourceCheck):

    def __init__(self) -> None:
        # This is the full description of your check
        description = "Ensure the CDN Enables the Https endpoint"

        # This is the Unique ID for your check
        id = "CKV_AZURE_200"

        # These are the Terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ['azurerm_cdn_endpoint_custom_domain']

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        insecure = ['None', 'TLS10']
        if 'cdn_managed_https' in conf and isinstance(conf.get('cdn_managed_https'), list):
            cdn = conf.get('cdn_managed_https')[0]
            if cdn['tls_version'][0] in insecure:
                return CheckResult.FAILED
        if 'user_managed_https' in conf and isinstance(conf.get('user_managed_https'), list):
            user = conf.get('user_managed_https')[0]
            if user['tls_version'][0] in insecure:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = CDNTLSProtocol12()

from checkov.common.models.enums import CheckCategories
from typing import Any
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CloudsearchDomainTLS(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Cloudsearch is using latest TLS"
        id = "CKV_AWS_218"
        supported_resources = ("aws_cloudsearch_domain",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "endpoint_options/[0]/tls_security_policy"

    def get_expected_value(self) -> Any:
        return "Policy-Min-TLS-1-2-2019-07"


check = CloudsearchDomainTLS()

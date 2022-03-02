from checkov.common.models.enums import CheckCategories
from typing import Any
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CloudsearchDomainEnforceHttps(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Cloudsearch is using https"
        id = "CKV_AWS_220"
        supported_resources = ["aws_cloudsearch_domain"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "endpoint_options/[0]/enforce_https"

    def get_expected_value(self) -> bool:
        return True


check = CloudsearchDomainEnforceHttps()
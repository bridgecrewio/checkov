from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DAXEndpointTLS(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure DAX cluster endpoint is using TLS"
        id = "CKV_AWS_239"
        supported_resources = ["aws_dax_cluster"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "cluster_endpoint_encryption_type"

    def get_expected_value(self) -> str:
        return "TLS"


check = DAXEndpointTLS()

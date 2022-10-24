from checkov.common.models.enums import CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ElasticsearchDomainEnforceHTTPS(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Elasticsearch Domain enforces HTTPS"
        id = "CKV_AWS_83"
        supported_resources = ("AWS::Elasticsearch::Domain",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/DomainEndpointOptions/EnforceHTTPS"


check = ElasticsearchDomainEnforceHTTPS()

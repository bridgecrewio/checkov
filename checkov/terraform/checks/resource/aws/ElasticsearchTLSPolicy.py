from typing import List, Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ElasticsearchTLSPolicy(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Verify Elasticsearch domain is using an up to date TLS policy"
        id = "CKV_AWS_228"
        supported_resources = ("aws_elasticsearch_domain", "aws_opensearch_domain")
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "domain_endpoint_options/[0]/tls_security_policy"

    def get_expected_values(self) -> List[Any]:
        return ["Policy-Min-TLS-1-2-2019-07", "Policy-Min-TLS-1-2-PFS-2023-10"]

    def get_expected_value(self) -> Any:
        return "Policy-Min-TLS-1-2-PFS-2023-10"


check = ElasticsearchTLSPolicy()

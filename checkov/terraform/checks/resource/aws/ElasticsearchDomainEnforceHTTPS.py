from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ElasticsearchDomainEnforceHTTPS(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure Elasticsearch Domain enforces HTTPS"
        id = "CKV_AWS_83"
        supported_resources = ['aws_elasticsearch_domain', 'aws_opensearch_domain']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "domain_endpoint_options/[0]/enforce_https"


check = ElasticsearchDomainEnforceHTTPS()

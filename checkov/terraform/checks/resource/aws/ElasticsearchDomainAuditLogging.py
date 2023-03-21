from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class ElasticsearchDomainAuditLogging(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure Elasticsearch Domain Audit Logging is enabled"
        id = "CKV_AWS_317"
        supported_resources = ['aws_elasticsearch_domain', 'aws_opensearch_domain']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "log_publishing_options/[0]/log_type/[0]"

    def get_expected_values(self):
        return "AUDIT_LOGS"


check = ElasticsearchDomainAuditLogging()

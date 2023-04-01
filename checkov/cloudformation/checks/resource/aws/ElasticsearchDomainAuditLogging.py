from checkov.common.models.enums import CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ElasticsearchDomainAuditLogging(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Elasticsearch Domain Audit Logging is enabled"
        id = "CKV_AWS_317"
        supported_resources = ("AWS::Elasticsearch::Domain", "AWS::OpenSearchService::Domain")
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/LogPublishingOptions/AUDIT_LOGS/Enabled"


check = ElasticsearchDomainAuditLogging()

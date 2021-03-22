from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ElasticsearchDomainLogging(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Elasticsearch Domain Logging is enabled"
        id = "CKV_AWS_84"
        supported_resources = ['AWS::Elasticsearch::Domain']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/LogPublishingOptions/AUDIT_LOGS/Enabled'

check = ElasticsearchDomainLogging()

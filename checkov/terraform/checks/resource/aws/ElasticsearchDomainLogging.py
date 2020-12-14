from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class ElasticsearchDomainLogging(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure Elasticsearch Domain Logging is enabled"
        id = "CKV_AWS_84"
        supported_resources = ['aws_elasticsearch_domain']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "log_publishing_options/[0]/cloudwatch_log_group_arn"

    def get_expected_value(self):
        return ANY_VALUE


check = ElasticsearchDomainLogging()

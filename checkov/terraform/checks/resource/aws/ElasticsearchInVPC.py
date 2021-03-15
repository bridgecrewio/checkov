from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ElasticsearchInVPC(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that Elasticsearch is configured inside a VPC"
        id = "CKV_AWS_137"
        supported_resources = ['aws_elasticsearch_domain']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "vpc_options"

    def get_expected_value(self):
        return ANY_VALUE


check = ElasticsearchInVPC()

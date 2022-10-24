from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ElasticsearchDefaultSG(BaseResourceValueCheck):

    def __init__(self):
        """
        If an ES cluster is does not have its Security group specified it tries to use the default SG
        and that can never be right.
        """
        name = "Ensure that Elasticsearch is not using the default Security Group"
        id = "CKV_AWS_248"
        supported_resources = ['aws_elasticsearch_domain', 'aws_opensearch_domain']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "vpc_options/[0]/security_group_ids"

    def get_expected_value(self):
        return ANY_VALUE


check = ElasticsearchDefaultSG()

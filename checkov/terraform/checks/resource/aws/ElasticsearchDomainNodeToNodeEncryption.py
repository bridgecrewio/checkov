from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ElasticsearchDomainNodeToNodeEncryption(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure Elasticsearch Domain enforces Node To Node Encryption"
        id = "CKV_AWS_157"
        supported_resources = ['aws_elasticsearch_domain']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "node_to_node_encryption/[0]/enabled"


check = ElasticsearchDomainNodeToNodeEncryption()

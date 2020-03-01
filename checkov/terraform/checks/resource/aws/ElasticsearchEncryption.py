from checkov.terraform.checks.resource.BaseResourceBooleanValueCheck import BaseResourceBooleanValueCheck
from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class ElasticsearchEncryption(BaseResourceBooleanValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the Elasticsearch is securely encrypted at rest"
        id = "CKV_AWS_5"
        supported_resources = ['aws_elasticsearch_domain']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "encrypt_at_rest/[0]/enabled"


check = ElasticsearchEncryption()

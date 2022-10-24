from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class ElasticsearchEncryptionWithCMK(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure all data stored in the Elasticsearch is encrypted with a CMK"
        id = "CKV_AWS_247"
        supported_resources = ('aws_elasticsearch_domain', 'aws_opensearch_domain')
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "encrypt_at_rest/[0]/kms_key_id"

    def get_expected_value(self):
        return ANY_VALUE


check = ElasticsearchEncryptionWithCMK()

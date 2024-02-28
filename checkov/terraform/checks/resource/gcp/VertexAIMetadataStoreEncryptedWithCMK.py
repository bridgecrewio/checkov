from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class VertexAIMetadataStoreEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Vertex AI Metadata Store uses a CMK (Customer Managed Key)"
        id = "CKV_GCP_96"
        supported_resources = ['google_vertex_ai_metadata_store']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'encryption_spec/[0]/kms_key_name'

    def get_expected_value(self):
        return ANY_VALUE


check = VertexAIMetadataStoreEncryptedWithCMK()

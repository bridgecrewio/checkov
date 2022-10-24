from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class ArtifactRegistryEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Artifact Registry Repositories are encrypted with Customer Supplied Encryption Keys (CSEK)"
        id = "CKV_GCP_84"
        supported_resources = ['google_artifact_registry_repository']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'kms_key_name'

    def get_expected_value(self):
        return ANY_VALUE


check = ArtifactRegistryEncryptedWithCMK()

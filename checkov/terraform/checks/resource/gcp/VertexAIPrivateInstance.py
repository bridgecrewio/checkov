from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class VertexAIPrivateInstance(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Vertex AI instances are private"
        id = "CKV_GCP_89"
        supported_resources = ['google_notebooks_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'no_public_ip'

    # Accounts for if key is present but is set to False
    def get_expected_value(self):
        return True

check = VertexAIPrivateInstance()

from typing import List

from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class GoogleVertexAINotebookShieldedVM(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Vertex AI Notebook instances are launched with Shielded VM enabled"
        id = "CKV_GCP_126"
        supported_resources = ['google_notebooks_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'shielded_instance_config/[0]/enable_vtpm'

    def get_forbidden_values(self) -> List[bool]:
        return [False]


check = GoogleVertexAINotebookShieldedVM()

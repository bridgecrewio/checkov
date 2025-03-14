from typing import List

from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class VertexAINotebookEnsureIntegrityMonitoring(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Integrity Monitoring for Shielded Vertex AI Notebook Instances is Enabled"
        id = "CKV_GCP_127"
        supported_resources = ['google_notebooks_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'shielded_instance_config/[0]/enable_integrity_monitoring'

    def get_forbidden_values(self) -> List[bool]:
        return [False]


check = VertexAINotebookEnsureIntegrityMonitoring()

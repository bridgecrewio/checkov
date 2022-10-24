from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories
from typing import List, Any


class NeptuneClusterInstancePublic(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure Neptune Cluster instance is not publicly available"
        id = "CKV_AWS_102"
        supported_resources = ['aws_neptune_cluster_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'publicly_accessible/[0]'

    def get_forbidden_values(self) -> List[Any]:
        return [True]


check = NeptuneClusterInstancePublic()

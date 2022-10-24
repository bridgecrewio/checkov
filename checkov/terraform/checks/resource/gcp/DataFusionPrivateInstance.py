from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DataFusionPrivateInstance(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Data fusion instances are private"
        id = "CKV_GCP_87"
        supported_resources = ['google_data_fusion_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'private_instance'


check = DataFusionPrivateInstance()

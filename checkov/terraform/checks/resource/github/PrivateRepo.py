from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories

class PrivateRepo(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Repository is Private"
        id = "CKV_GIT_1"
        supported_resources = ['github_repository']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "private"


check = PrivateRepo()

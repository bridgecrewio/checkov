from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GoogleComputeProjectOSLogin(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure oslogin is enabled for a Project"
        id = "CKV_GCP_33"
        supported_resources = ['google_compute_project_metadata']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'metadata/[0]/enable-oslogin'

    def get_expected_value(self):
        return "TRUE"


check = GoogleComputeProjectOSLogin()

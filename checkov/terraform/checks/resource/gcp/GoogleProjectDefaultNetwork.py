from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GoogleProjectDefaultNetwork(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that the default network does not exist in a project"
        id = "CKV_GCP_27"
        supported_resources = ['google_project']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        """
        https://www.terraform.io/docs/providers/google/r/google_project.html
        :param conf: google_project configuration
        :return: <CheckResult>
        """
        return 'auto_create_network/[0]'

    def get_expected_value(self):
        return False


check = GoogleProjectDefaultNetwork()

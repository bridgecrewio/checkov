from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class CloudFunctionsShouldNotBePublic(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Cloud functions should not be public"
        id = "CKV_GCP_107"
        supported_resources = ['google_cloudfunctions_function_iam_member']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'member'

    def get_forbidden_values(self):
        return "allUsers"


check = CloudFunctionsShouldNotBePublic()


from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class IAMUserRootAccessKeys(BaseResourceNegativeValueCheck):

    def __init__(self):
        name = "Ensure IAM root user doesnt have Access keys"
        id = "CKV_AWS_348"
        supported_resources = ['aws_iam_access_key']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "user"

    def get_forbidden_values(self):
        return ["root"]


check = IAMUserRootAccessKeys()

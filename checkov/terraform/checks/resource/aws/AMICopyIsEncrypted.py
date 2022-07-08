from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class AMICopyIsEncrypted(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that copied AMIs are encrypted"
        id = "CKV_AWS_235"
        supported_resources = ['aws_ami_copy']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "encrypted"


check = AMICopyIsEncrypted()

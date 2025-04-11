from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class EFSEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure EFS file systems are encrypted"
        id = "CKV_AWS_42"
        supported_resources = ("awscc_efs_file_system",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "encrypted"

    def get_expected_value(self):
        return True


check = EFSEncryption()

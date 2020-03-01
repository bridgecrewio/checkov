from checkov.terraform.checks.resource.BaseResourceBooleanValueCheck import BaseResourceBooleanValueCheck
from checkov.terraform.models.enums import CheckCategories


class EBSEncryption(BaseResourceBooleanValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the EBS is securely encrypted "
        id = "CKV_AWS_3"
        supported_resources = ['aws_ebs_volume']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "encrypted"


check = EBSEncryption()

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DAXEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure DAX is encrypted at rest (default is unencrypted)"
        id = "CKV_AWS_47"
        supported_resources = ['aws_dax_cluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "server_side_encryption/[0]/enabled"


check = DAXEncryption()

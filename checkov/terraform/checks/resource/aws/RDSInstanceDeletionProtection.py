from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class RDSInstanceDeletionProtection(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that AWS database instances have deletion protection enabled"
        id = "CKV_AWS_293"
        supported_resources = ['aws_db_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'deletion_protection'


check = RDSInstanceDeletionProtection()

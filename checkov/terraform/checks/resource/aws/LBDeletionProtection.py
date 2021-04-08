from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class LBDeletionProtection(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that Load Balancer has deletion protection enabled"
        id = "CKV_AWS_113"
        supported_resources = ['aws_lb', 'aws_alb']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'enable_deletion_protection'


check = LBDeletionProtection()

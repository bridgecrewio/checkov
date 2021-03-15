from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class EC2EBSOptimized(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that EC2 is EBS optimized"
        id = "CKV_AWS_135"
        supported_resources = ['aws_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "ebs_optimized"


check = EC2EBSOptimized()

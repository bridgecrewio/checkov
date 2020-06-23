from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class EKSPublicAccess(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Amazon EKS public endpoint disabled"
        id = "CKV_AWS_39"
        supported_resources = ['aws_eks_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'vpc_config/[0]/endpoint_public_access/[0]/endpoint_public_access'

    def get_expected_value(self):
        return False


check = EKSPublicAccess()

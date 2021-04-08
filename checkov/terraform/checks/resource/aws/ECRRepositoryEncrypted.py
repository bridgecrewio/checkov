from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ECRRepositoryEncrypted(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that ECR repositories are encrypted using KMS"
        id = "CKV_AWS_136"
        supported_resources = ['aws_ecr_repository']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'encryption_configuration/[0]/encryption_type'

    def get_expected_value(self):
        return "KMS"


check = ECRRepositoryEncrypted()

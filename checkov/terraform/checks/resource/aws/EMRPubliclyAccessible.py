from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class EMRPubliclyAccessible(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure AWS EMR block public access setting is enabled"
        id = "CKV_AWS_390"
        supported_resources = ['aws_emr_block_public_access_configuration']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "block_public_security_group_rules"


check = EMRPubliclyAccessible()

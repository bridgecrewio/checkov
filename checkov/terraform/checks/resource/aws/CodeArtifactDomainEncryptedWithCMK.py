from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class CodeArtifactDomainEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure CodeArtifact Domain is encrypted by KMS using a customer managed Key (CMK)"
        id = "CKV_AWS_221"
        supported_resources = ['aws_codeartifact_domain']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        """
        Why not be consistent and use kms_key_id ..sigh.
        """
        return "encryption_key"

    def get_expected_value(self):
        return ANY_VALUE


check = CodeArtifactDomainEncryptedWithCMK()

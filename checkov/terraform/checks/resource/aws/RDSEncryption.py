from checkov.terraform.checks.resource.BaseResourceBooleanValueCheck import BaseResourceBooleanValueCheck
from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class RDSEncryption(BaseResourceBooleanValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the RDS is securely encrypted at rest"
        id = "CKV_AWS_16"
        supported_resources = ['aws_db_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "storage_encrypted"


check = RDSEncryption()

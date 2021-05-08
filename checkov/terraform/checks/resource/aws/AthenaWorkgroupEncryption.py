from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AthenaWorkgroupEncryption(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that Athena Workgroup is encrypted"
        id = "CKV_AWS_159"
        supported_resources = ['aws_athena_workgroup']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "configuration/[0]/result_configuration/[0]/encryption_configuration/[0]/encryption_option"

    def get_expected_value(self):
        return ANY_VALUE

check = AthenaWorkgroupEncryption()

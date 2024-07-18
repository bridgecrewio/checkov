from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import \
    BaseResourceValueCheck


class CBSEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the CBS is securely encrypted"
        id = "CKV_TC_1"
        supported_resources = ['tencentcloud_cbs_storage']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "encrypt"

    def get_expected_value(self) -> bool:
        return True


check = CBSEncryption()

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class EFSEncryptionEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure NAS is securely encrypted"
        id = "CKV_NCP_14"
        supported_resources = ("ncloud_nas_volume",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "is_encrypted_volume"


check = EFSEncryptionEnabled()

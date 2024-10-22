from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class KeyExpirationDate(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that the expiration date is set on all keys"
        id = "CKV_AZURE_40"
        supported_resources = ['Microsoft.KeyVault/vaults/keys']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'properties/rotationPolicy/attributes/expiryTime'

    def get_expected_value(self) -> str:
        return ANY_VALUE


check = KeyExpirationDate()

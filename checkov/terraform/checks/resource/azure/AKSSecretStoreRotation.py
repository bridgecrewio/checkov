from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AkSSecretStoreRotation(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure autorotation of Secrets Store CSI Driver secrets for AKS clusters"
        id = "CKV_AZURE_172"
        supported_resources = ("azurerm_kubernetes_cluster",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "key_vault_secrets_provider/secret_rotation_enabled"


check = AkSSecretStoreRotation()

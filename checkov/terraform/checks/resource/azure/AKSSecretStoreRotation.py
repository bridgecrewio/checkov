from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AkSSecretStoreRotation(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure autorotation of Secrets Store CSI Driver secrets for AKS clusters"
        id = "CKV_AZURE_172"
        supported_resources = ("azurerm_kubernetes_cluster",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("key_vault_secrets_provider") and isinstance(conf.get("key_vault_secrets_provider"), list):
            provider = conf.get("key_vault_secrets_provider")[0]
            if provider.get("secret_rotation_enabled") == [True]:
                return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.UNKNOWN


check = AkSSecretStoreRotation()

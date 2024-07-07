from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class SynapseWorkspaceCMKEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Azure Synapse Workspace is encrypted with a CMK"
        id = "CKV_AZURE_239"
        supported_resources = ['Microsoft.Synapse/workspaces']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "encryption" not in conf:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = SynapseWorkspaceCMKEncryption()

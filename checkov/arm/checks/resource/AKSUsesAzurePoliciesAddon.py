from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceCheck


class AKSUsesAzurePoliciesAddon(BaseResourceCheck):
    def __init__(self) -> None:
        # האם צריך להוסיף שורה זו, כדי שיהיה את מי לעדכן???
        self.evaluatedKey = None
        name = "Ensure that AKS uses Azure Policies Add-on"
        id = "CKV_AZURE_116"
        supported_resources = ("Microsoft.ContainerService/managedClusters",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources
        )

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        # since Azure provider v2.97.0
        properties = conf.get("properties")
        if not properties:
            return CheckResult.FAILED
        self.evaluatedKey = "addonProfiles"
        addonProfiles = properties.get("addonProfiles")
        if addonProfiles:
            azurePolicy = addonProfiles.get("azurePolicy")
            if azurePolicy:
                enabled = azurePolicy.get("enabled")
                if enabled:
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = AKSUsesAzurePoliciesAddon()

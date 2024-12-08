from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AKSEncryptionAtHostEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        With host-based encryption, the data stored on the VM host of
        your AKS agent nodes' VMs is encrypted at rest and flows encrypted to the Storage service.
        This means the temp disks are encrypted at rest with platform-managed keys.
        The cache of OS and data disks is encrypted at rest with either platform-managed keys
        or customer-managed keys depending on the encryption type set on those disks.
        """
        name = "Ensure that the AKS cluster encrypt temp disks, caches, and data flows "
        name += "between Compute and Storage resources"
        id = "CKV_AZURE_227"
        supported_resources = ["Microsoft.ContainerService/managedClusters",
                               "Microsoft.ContainerService/managedClusters/agentPools"]
        categories = [CheckCategories.KUBERNETES, ]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.FAILED,
        )

    def get_inspected_key(self) -> str:
        if self.entity_type == "Microsoft.ContainerService/managedClusters":
            return "properties/agentPoolProfiles/[0]/enableEncryptionAtHost"
        else:
            return "properties/enableEncryptionAtHost"

    def get_expected_value(self) -> bool:
        return True


check = AKSEncryptionAtHostEnabled()

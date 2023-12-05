from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class AKSEphemeralOSDisks(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        Temporary data can contain sensitive data at some points, by using ephemeral disks,
        we ensure that data written to OS disk is stored on local VM storage and isn't persisted to Azure Storage

        Azure automatically replicates data stored in the managed OS disk of a virtual machine to Azure storage
        to avoid data loss in case the virtual machine needs to be relocated to another host.
        Generally speaking, containers are not designed to have local state persisted to the managed OS disk,
        hence this behavior offers limited value to AKS hosted while providing some drawbacks,
        including slower node provisioning and higher read/write latency.

        Ephemeral disks allow us also to have faster cluster operations like scale or upgrade
        due to faster re-imaging and boot times.
        """
        name = "Ensure ephemeral disks are used for OS disks"
        id = "CKV_AZURE_226"
        supported_resources = ("azurerm_kubernetes_cluster",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "default_node_pool/[0]/os_disk_type"

    def get_expected_value(self) -> Any:
        return "Ephemeral"


check = AKSEphemeralOSDisks()

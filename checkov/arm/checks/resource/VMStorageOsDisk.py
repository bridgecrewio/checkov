from typing import Any, Dict

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceCheck


class VMStorageOsDisk(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Virtual Machines use managed disks"
        id = "CKV_AZURE_92"
        supported_resources = ("Microsoft.Compute/virtualMachines",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        properties = conf.get('properties')
        if not properties or not isinstance(properties, dict):
            return CheckResult.PASSED
        storage_profile = properties.get('storageProfile')
        if not storage_profile or not isinstance(storage_profile, dict):
            return CheckResult.PASSED
        os_disk = storage_profile.get('osDisk')
        data_disks = list(storage_profile.get('dataDisks', []))
        if os_disk and isinstance(os_disk, dict) and "vhd" in os_disk:
            self.evaluated_keys = ['os_disk']
            return CheckResult.FAILED
        if data_disks and any(isinstance(data_disk, dict) and "vhd" in data_disk for data_disk in data_disks):
            self.evaluated_keys = ['data_disks']
            return CheckResult.FAILED
        self.evaluated_keys = ['os_disk'] if os_disk else []
        if data_disks:
            self.evaluated_keys.append('data_disks')
        return CheckResult.PASSED


check = VMStorageOsDisk()

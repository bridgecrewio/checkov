from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class NetworkInterfaceEnableIPForwarding(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Azure File Sync disables public network access"
        id = "CKV_AZURE_64"
        supported_resources = ('Microsoft.StorageSync/storageSyncServices',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return 'properties/incoming_traffic_policy'

    def get_expected_value(self):
        return 'AllowVirtualNetworksOnly'


check = NetworkInterfaceEnableIPForwarding()

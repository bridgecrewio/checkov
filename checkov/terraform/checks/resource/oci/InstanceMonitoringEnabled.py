from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class InstanceMonitoringEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "OCI Compute Instance has monitoring disabled"
        id = "CKV_OCI_6"
        supported_resources = ['oci_core_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "agent_config/[0]/is_monitoring_disabled"

    def get_expected_value(self):
        return False


check = InstanceMonitoringEnabled()


from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class InstanceMonitoringEnabled(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure OCI Compute Instance has monitoring enabled"
        id = "CKV_OCI_6"
        supported_resources = ['oci_core_instance']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "agent_config/[0]/is_monitoring_disabled"

    def get_forbidden_values(self):
        return [True]

check = InstanceMonitoringEnabled()


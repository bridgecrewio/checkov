from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class PostgresSQLTreatDetectionEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that PostgreSQL server enables Threat detection policy"
        id = "CKV_AZURE_128"
        supported_resources = ['azurerm_postgresql_server']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "threat_detection_policy/[0]/enabled"


check = PostgresSQLTreatDetectionEnabled()

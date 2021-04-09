from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class MySQLTreatDetectionEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that My SQL server enables Threat detection policy"
        id = "CKV_AZURE_127"
        supported_resources = ['azurerm_mysql_server']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)


    def get_inspected_key(self):
        return "threat_detection_policy/enabled"


check = MySQLTreatDetectionEnabled()

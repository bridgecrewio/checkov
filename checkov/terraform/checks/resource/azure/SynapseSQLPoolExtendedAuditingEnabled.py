from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class SynapseSQLPoolExtendedAuditingEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure log monitoring is enabled for Synapse SQL Pool"
        id = "CKV_AZURE_240"
        supported_resources = ['synapse_sql_pool_extended_auditing_policy']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "log_monitoring_enabled"

    def get_expected_value(self):
        return True

check = SynapseSQLPoolExtendedAuditingEnabled()

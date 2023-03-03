from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class LogAuditRDSEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure log audit is enabled for RDS"
        id = "CKV_ALI_38"
        supported_resources = ("alicloud_log_audit",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "variable_map/[0]/rds_enabled"


check = LogAuditRDSEnabled()

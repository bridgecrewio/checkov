from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck

class PostgreSQLServerSSLEnforcementEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure 'Enforce SSL connection' is set to 'ENABLED' for PostgreSQL Database Server"
        id = "CKV_AZURE_29"
        supported_resources = ['Microsoft.DBforPostgreSQL/servers']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "properties" in conf:
            if "sslEnforcement" in conf["properties"]:
                if str(conf["properties"]["sslEnforcement"]).lower() == "enabled":
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = PostgreSQLServerSSLEnforcementEnabled()

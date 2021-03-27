import re

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import (
    BaseResourceCheck,
)

PORT_RANGE = re.compile("\d+-\d+")


class SQLServerNoPublicAccess(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no SQL Databases allow ingress from 0.0.0.0/0 (ANY IP)"
        id = "CKV_AZURE_11"
        supported_resources = [
            "azurerm_mariadb_firewall_rule",
            "azurerm_sql_firewall_rule",
            "azurerm_postgresql_firewall_rule",
            "azurerm_mysql_firewall_rule",
        ]
        categories = [CheckCategories.NETWORKING]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf):
        start_ip = conf.get("start_ip_address")
        if start_ip and start_ip[0] in ["0.0.0.0", "0.0.0.0/0"]:  # nosec
            return CheckResult.FAILED

        return CheckResult.PASSED


check = SQLServerNoPublicAccess()

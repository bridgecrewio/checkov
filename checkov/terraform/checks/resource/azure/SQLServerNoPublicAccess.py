from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
import re

PORT_RANGE = re.compile(r'\d+-\d+')


class SQLServerNoPublicAccess(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no SQL Databases allow ingress from 0.0.0.0/0 (ANY IP)"
        id = "CKV_AZURE_11"
        supported_resources = (
            'azurerm_mariadb_firewall_rule',
            'azurerm_sql_firewall_rule',
            'azurerm_postgresql_firewall_rule',
            'azurerm_mysql_firewall_rule',
            'azurerm_mysql_flexible_server_firewall_rule',
            'azurerm_mssql_firewall_rule',
        )
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        self.evaluated_keys = ['start_ip_address']
        if 'end_ip_address' in conf:
            self.evaluated_keys.append('end_ip_address')
        if ('start_ip_address' in conf and conf['start_ip_address'][0] in ('0.0.0.0', '0.0.0.0/0') and  # nosec
                'end_ip_address' in conf and conf['end_ip_address'][0] == '255.255.255.255'):
            return CheckResult.FAILED
        return CheckResult.PASSED


check = SQLServerNoPublicAccess()

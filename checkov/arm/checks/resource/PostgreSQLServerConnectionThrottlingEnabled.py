from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class PostgreSQLServerConnectionThrottlingEnabled(BaseResourceCheck):
    def __init__(self) -> None:
        # https://docs.microsoft.com/en-us/azure/templates/microsoft.dbforpostgresql/servers
        # https://docs.microsoft.com/en-us/azure/templates/microsoft.dbforpostgresql/servers/configurations
        name = "Ensure server parameter 'connection_throttling' is set to 'ON' for PostgreSQL Database Server"
        id = "CKV_AZURE_32"
        supported_resources = ('Microsoft.DBforPostgreSQL/servers/configurations', 'configurations')
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "type" in conf:
            if conf["type"] == "Microsoft.DBforPostgreSQL/servers/configurations":
                if "name" in conf and conf["name"] == "connection_throttling":
                    if "properties" in conf:
                        if "value" in conf["properties"] and \
                                conf["properties"]["value"].lower() == "on":
                            return CheckResult.PASSED
                    return CheckResult.FAILED
                # If name not connection_throttling - don't report (neither pass nor fail)
            elif conf["type"] == "configurations":
                if "name" in conf and conf["name"] == "connection_throttling":
                    if "parent_type" in conf:
                        if conf["parent_type"] == "Microsoft.DBforPostgreSQL/servers":
                            if "properties" in conf:
                                if "value" in conf["properties"] and \
                                        conf["properties"]["value"].lower() == "on":
                                    return CheckResult.PASSED
                    return CheckResult.FAILED
                # If name not connection_throttling - don't report (neither pass nor fail)
        else:
            return CheckResult.FAILED


check = PostgreSQLServerConnectionThrottlingEnabled()

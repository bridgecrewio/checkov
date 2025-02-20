from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class PostgreSQLServerLogCheckpointsEnabled(BaseResourceCheck):
    def __init__(self) -> None:
        # https://docs.microsoft.com/en-us/azure/templates/microsoft.dbforpostgresql/servers
        # https://docs.microsoft.com/en-us/azure/templates/microsoft.dbforpostgresql/servers/configurations
        # https://docs.microsoft.com/en-us/rest/api/postgresql/configurations/listbyserver#examples
        name = "Ensure server parameter 'log_checkpoints' is set to 'ON' for PostgreSQL Database Server"
        id = "CKV_AZURE_30"
        supported_resources = ('Microsoft.DBforPostgreSQL/servers/configurations', 'configurations')
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["properties"]
        if "type" in conf:
            if conf["type"] == "Microsoft.DBforPostgreSQL/servers/configurations":
                if "name" in conf and conf["name"] == "log_checkpoints":
                    if "properties" in conf:
                        if "value" in conf["properties"] and \
                                conf["properties"]["value"].lower() == "on":
                            return CheckResult.PASSED
                    self.evaluated_keys.append("properties/value")
                    return CheckResult.FAILED
            elif conf["type"] == "configurations":
                if "name" in conf and conf["name"] == "log_checkpoints":
                    if "parent_type" in conf:
                        if conf["parent_type"] == "Microsoft.DBforPostgreSQL/servers":
                            if "properties" in conf:
                                if "value" in conf["properties"] and \
                                        conf["properties"]["value"].lower() == "on":
                                    return CheckResult.PASSED
                    self.evaluated_keys.append("properties/value")
                    return CheckResult.FAILED
        else:
            return CheckResult.FAILED

        # If name not connection_throttling - don't report (neither pass nor fail)
        return CheckResult.UNKNOWN


check = PostgreSQLServerLogCheckpointsEnabled()

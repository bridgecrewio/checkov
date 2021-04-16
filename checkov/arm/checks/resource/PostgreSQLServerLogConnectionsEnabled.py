from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck

# https://docs.microsoft.com/en-us/azure/templates/microsoft.dbforpostgresql/servers
# https://docs.microsoft.com/en-us/azure/templates/microsoft.dbforpostgresql/servers/configurations
# https://docs.microsoft.com/en-us/rest/api/postgresql/configurations/listbyserver#examples

class PostgreSQLServerLogConnectionsEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure configuration 'log_connections' is set to 'ON' for PostgreSQL Database Server"
        id = "CKV_AZURE_31"
        supported_resources = ['Microsoft.DBforPostgreSQL/servers/configurations', 'configurations']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "type" in conf:
            if conf["type"] == "Microsoft.DBforPostgreSQL/servers/configurations":
                if "name" in conf and conf["name"] == "log_connections":
                    if "properties" in conf:
                        if "value" in conf["properties"] and \
                                conf["properties"]["value"].lower() == "on":
                            return CheckResult.PASSED
                    return CheckResult.FAILED
                # If name not connection_throttling - don't report (neither pass nor fail)
            elif conf["type"] == "configurations":
                if "name" in conf and conf["name"] == "log_connections":
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

check = PostgreSQLServerLogConnectionsEnabled()

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck

# https://docs.microsoft.com/en-us/azure/templates/microsoft.dbforpostgresql/servers
# https://docs.microsoft.com/en-us/azure/templates/microsoft.dbforpostgresql/servers/configurations

class PostgreSQLServerConnectionThrottlingEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure server parameter 'connection_throttling' is set to 'ON' for PostgreSQL Database Server"
        id = "CKV_AZURE_32"
        supported_resources = ['Microsoft.DBforPostgreSQL/servers']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "resources" in conf:
            if conf["resources"]:
                for resource in conf["resources"]:
                    if "type" in resource:
                        if resource["type"] == "Microsoft.DBforPostgreSQL/servers/configurations" or \
                                resource["type"] == "configurations":
                            if "name" in resource and resource["name"] == "connection_throttling":
                                if "properties" in resource:
                                    if "value" in resource["properties"] and \
                                            resource["properties"]["value"].lower() == "on":
                                        return CheckResult.PASSED

        return CheckResult.FAILED

check = PostgreSQLServerConnectionThrottlingEnabled()

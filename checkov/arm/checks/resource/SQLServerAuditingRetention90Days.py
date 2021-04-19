from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck

# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2019-06-01-preview/servers
# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2017-03-01-preview/servers/databases/auditingsettings

class SQLServerAuditingRetention90Days(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that 'Auditing' Retention is 'greater than 90 days' for SQL servers"
        id = "CKV_AZURE_24"
        supported_resources = ['Microsoft.Sql/servers']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "resources" in conf:
            if conf["resources"]:
                for resource in conf["resources"]:
                    if "type" in resource:
                        if resource["type"] == "Microsoft.Sql servers/databases/auditingSettings" or \
                                resource["type"] == "auditingSettings":
                            if "properties" in resource:
                                if "state" in resource["properties"] and \
                                        resource["properties"]["state"].lower() == "enabled":
                                    if "retentionDays" in resource["properties"] and \
                                            int(resource["properties"]["retentionDays"]) >= 90:
                                                return CheckResult.PASSED

        return CheckResult.FAILED

check = SQLServerAuditingRetention90Days()

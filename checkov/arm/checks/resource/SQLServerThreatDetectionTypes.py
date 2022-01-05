from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2019-06-01-preview/servers
# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2017-03-01-preview/servers/securityalertpolicies

class SQLServerThreatDetectionTypes(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that 'Threat Detection types' is set to 'All'"
        id = "CKV_AZURE_25"
        supported_resources = ['Microsoft.Sql/servers/databases'] ###, 'Microsoft.Sql/servers']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "resources" in conf:
            if conf["resources"]:
                for resource in conf["resources"]:
                    if "type" in resource:
                        if resource["type"] == "Microsoft.Sql/servers/databases/securityAlertPolicies" or \
                                resource["type"] == "securityAlertPolicies":
                            if "properties" in resource:
                                if "state" in resource["properties"] and \
                                        resource["properties"]["state"].lower() == "enabled":
                                    if "disabledAlerts" in resource["properties"]:
                                        if resource["properties"]["disabledAlerts"] == "" or \
                                                resource["properties"]["disabledAlerts"] is None:
                                            return CheckResult.PASSED
                                    else:
                                        return CheckResult.PASSED

        return CheckResult.FAILED


check = SQLServerThreatDetectionTypes()

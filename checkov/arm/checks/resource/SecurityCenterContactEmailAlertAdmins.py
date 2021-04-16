from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck

# https://docs.microsoft.com/en-us/azure/templates/microsoft.security/securitycontacts

class SecurityCenterContactEmailAlertAdmins(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that 'Send email notification for high severity alerts' is set to 'On'"
        id = "CKV_AZURE_22"
        supported_resources = ['Microsoft.Security/securityContacts']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "properties" in conf:
            if "alertsToAdmins" in conf["properties"]:
                if str(conf["properties"]["alertsToAdmins"]).lower() == "on":
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = SecurityCenterContactEmailAlertAdmins()

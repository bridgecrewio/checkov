from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck

# https://docs.microsoft.com/en-us/azure/templates/microsoft.security/securitycontacts

class SecurityCenterContactEmailAlert(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that 'Send email notification for high severity alerts' is set to 'On'"
        id = "CKV_AZURE_21"
        supported_resources = ['Microsoft.Security/securityContacts']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "properties" in conf:
            if "alertNotifications" in conf["properties"]:
                if str(conf["properties"]["alertNotifications"]).lower() == "on":
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = SecurityCenterContactEmailAlert()

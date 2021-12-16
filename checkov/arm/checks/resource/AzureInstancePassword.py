from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class AzureInstancePassword(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Azure Instance does not use basic authentication(Use SSH Key Instead)"
        id = "CKV_AZURE_1"
        supported_resources = ['Microsoft.Compute/virtualMachines']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        properties = conf.get("properties")
        if isinstance(properties, dict):
            storage_profile = properties.get("storageProfile")
            if isinstance(storage_profile, dict):
                image_reference = storage_profile.get("imageReference")
                if isinstance(image_reference, dict):
                    publisher = image_reference.get("publisher")
                    if publisher and "windows" in publisher.lower():
                        # This check is not relevant to Windows systems
                        return CheckResult.PASSED

            os_profile = properties.get("osProfile")
            if isinstance(os_profile, dict):
                linux_conf = os_profile.get("linuxConfiguration")
                if isinstance(linux_conf, dict) and linux_conf.get("disablePasswordAuthentication"):
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = AzureInstancePassword()

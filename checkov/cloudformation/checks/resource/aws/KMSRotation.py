from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class KMSRotation(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure rotation for customer created CMKs is enabled"
        id = "CKV_AWS_7"
        supported_resources = ("AWS::KMS::Key",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/EnableKeyRotation"

    def scan_resource_conf(self, conf):
        # Only symmetric keys support auto rotation. The attribute is optional and defaults to symmetric.
        if 'Properties' in conf.keys():
            if 'KeySpec' in conf['Properties'].keys():
                spec = conf['Properties']['KeySpec']
                if not spec or 'SYMMETRIC_DEFAULT' in spec or 'HMAC' in spec:
                    print("Symmetric Key")
                    return super().scan_resource_conf(conf)
                else:
                    print("Found Assymetric Key")
                    return CheckResult.PASSED
        return super().scan_resource_conf(conf)


check = KMSRotation()

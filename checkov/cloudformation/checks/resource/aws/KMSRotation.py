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
        properties = conf.get("Properties")
        if properties and isinstance(properties, dict):
            spec = properties.get("KeySpec")
            if spec and isinstance(spec, str):
                if 'SYMMETRIC_DEFAULT' not in spec and 'HMAC' not in spec:
                    return CheckResult.UNKNOWN
        return super().scan_resource_conf(conf)


check = KMSRotation()

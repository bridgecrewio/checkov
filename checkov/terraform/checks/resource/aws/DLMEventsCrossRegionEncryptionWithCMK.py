from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DLMEventsCrossRegionEncryptionWithCMK(BaseResourceCheck):
    def __init__(self):
        name = "Ensure DLM cross region events are encrypted with Customer Managed Key"
        id = "CKV_AWS_254"
        supported_resources = ['aws_dlm_lifecycle_policy']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("policy_details") and isinstance(conf.get("policy_details"), list):
            policy = conf.get("policy_details")[0]
            if policy.get("action") and isinstance(policy.get("action"), list):
                actions = policy.get("action")
                for idx, action in enumerate(actions):
                    if not isinstance(action, dict) or not action:
                        return CheckResult.UNKNOWN
                    if action.get("cross_region_copy") and isinstance(action.get("cross_region_copy"), list):
                        cross = action.get("cross_region_copy")[0]
                        if cross.get("encryption_configuration") and isinstance(cross.get("encryption_configuration"), list):
                            config = cross.get("encryption_configuration")[0]
                            if config.get("encryption") == [True] and config.get("cmk_arn"):
                                return CheckResult.PASSED
                        self.evaluated_keys = [f"policy_details/action/{idx}/cross_region_copy/encryption_configuration"]
                        return CheckResult.FAILED
                    return CheckResult.UNKNOWN
                return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = DLMEventsCrossRegionEncryptionWithCMK()

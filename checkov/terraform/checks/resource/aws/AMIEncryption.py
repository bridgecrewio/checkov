from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AMIEncryptionWithCMK(BaseResourceCheck):
    def __init__(self):
        name = "Ensure AMIs are encrypted using KMS CMKs"
        id = "CKV_AWS_204"
        supported_resources = ['aws_ami']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get('ebs_block_device'):
            mappings = conf.get('ebs_block_device')
            self.evaluated_keys = ["ebs_block_device"]
            for mapping_idx, mapping in enumerate(mappings):
                if not mapping.get("snapshot_id"):
                    if not mapping.get("encrypted"):
                        return CheckResult.FAILED
                    if mapping.get("encrypted")[0] is False:
                        self.evaluated_keys.append(f"ebs_block_device/[{mapping_idx}]/encrypted")
                        return CheckResult.FAILED
        # pass thru
        return CheckResult.PASSED


check = AMIEncryptionWithCMK()

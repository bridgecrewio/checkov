from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DiskIsEncrypted(BaseResourceCheck):
    def __init__(self):
        # This is the full description of your check
        description = "Make sure that `tencentcloud_cbs_storage` resources have set `encrypt` field to `true`"

        # This is the Unique ID for your check
        id = "CKV_TENCENT_1"

        # These are the terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ['tencentcloud_cbs_storage']

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Replace this with the custom logic for your check
        if conf.get("snapshot_id"):
            return CheckResult.UNKNOWN
        if conf.get("encrypt") and conf.get("encrypt") == [True]:
            return CheckResult.PASSED

        return CheckResult.FAILED


check = DiskIsEncrypted()
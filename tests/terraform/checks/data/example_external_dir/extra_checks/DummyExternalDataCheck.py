from checkov.terraform.checks.data.base_check import BaseDataCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class DummyExternalDataCheck(BaseDataCheck):
    def __init__(self):
        name = "check for terraform data entity"
        id = "CKV_AWS_999"
        supported_resources = ['aws_iam_policy_document']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_data=supported_resources)

    def scan_data_conf(self, conf):
        return CheckResult.PASSED


scanner = DummyExternalDataCheck()

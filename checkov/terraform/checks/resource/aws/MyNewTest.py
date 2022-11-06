from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class MyNewTest(BaseResourceCheck):
    def __init__(self):
        # This is the full description of your check
        description = "Ensure that X does Y..."

        # This is the Unique ID for your check
        id = "CKV_AWS_274"

        # These are the terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ['aws_iam_policy']

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = [CheckCategories.IAM]
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Replace this with the custom logic for your check
        if 'policy' in conf.keys():
            return CheckResult.FAILED

        return CheckResult.PASSED


check = MyNewTest()
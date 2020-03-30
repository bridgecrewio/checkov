from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class UserPolicyAttachment(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all data stored in the SQS queue  is encrypted"
        id = "CKV_AWS_50"
        supported_resources = ['aws_iam_user_policy', 'aws_iam_user_policy_attachment']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Any attachment of a policy, either an inline policy or a managed policy, is a violation.
        return CheckResult.FAILED


check = UserPolicyAttachment()

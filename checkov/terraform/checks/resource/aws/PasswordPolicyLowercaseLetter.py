from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class PasswordPolicyLowercaseLetter(BaseResourceCheck):
    def __init__(self):
        name = "Ensure IAM password policy requires at least one lowercase letter"
        id = "CKV_AWS_11"
        supported_resources = ['aws_iam_account_password_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            validates iam password policy
            https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy.html
        :param conf: aws_iam_account_password_policy configuration
        :return: <CheckResult>
        """
        key = 'require_lowercase_characters'
        if key in conf.keys():
            if conf[key][0]:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = PasswordPolicyLowercaseLetter()

from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class PasswordPolicyUppcaseLetter(BaseResourceCheck):
    def __init__(self):
        name = "Ensure IAM password policy requires at least one uppercase letter"
        id = "CKV_AWS_15"
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
        key = 'require_uppercase_characters'
        if key in conf.keys():
            if conf[key][0]:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = PasswordPolicyUppcaseLetter()

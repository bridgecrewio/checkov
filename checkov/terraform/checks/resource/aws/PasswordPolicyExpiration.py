from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_int


class PasswordPolicyExpiration(BaseResourceCheck):
    def __init__(self):
        name = "Ensure IAM password policy expires passwords within 90 days or less"
        id = "CKV_AWS_9"
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
        key = 'max_password_age'
        if key in conf.keys():
            max_age = force_int(conf[key][0])
            if max_age and max_age <= 90:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = PasswordPolicyExpiration()

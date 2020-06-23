from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.util.type_forcers import force_int


class PasswordPolicyReuse(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure IAM password policy prevents password reuse"
        id = "CKV_AWS_13"
        supported_resources = ['aws_iam_account_password_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'password_reuse_prevention'

    def get_expected_value(self):
        return 24

    def scan_resource_conf(self, conf):
        """
            validates iam password policy
            https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy.html
        :param conf: aws_iam_account_password_policy configuration
        :return: <CheckResult>
        """
        key = 'password_reuse_prevention'
        if key in conf.keys():
            if not (force_int(conf[key][0]) and force_int(conf[key][0]) < 24):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = PasswordPolicyReuse()

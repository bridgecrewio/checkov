from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.util.type_forcers import force_int


class PasswordPolicyLength(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure IAM password policy requires minimum length of 14 or greater"
        id = "CKV_AWS_10"
        supported_resources = ['aws_iam_account_password_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'minimum_password_length'

    def get_expected_value(self):
        return 14

    def scan_resource_conf(self, conf):
        """
            validates iam password policy
            https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy.html
        :param conf: aws_iam_account_password_policy configuration
        :return: <CheckResult>
        """
        key = 'minimum_password_length'
        if key in conf.keys():
            length = conf[key][0]
            if self._is_variable_dependant(length):
                return CheckResult.UNKNOWN
            length = force_int(length)
            if not (length and length < 14):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = PasswordPolicyLength()

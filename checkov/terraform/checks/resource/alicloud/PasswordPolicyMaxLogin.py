from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.util.type_forcers import force_int


class PasswordPolicyMaxLogin(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Ram Account Password Policy Max Login Attempts not > 5"
        id = "CKV_ALI_23"
        supported_resources = ['alicloud_ram_account_password_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return 'max_login_attempts'

    def get_expected_value(self):
        return 3

    def scan_resource_conf(self, conf):
        """
            validates ram password policy
            https://registry.terraform.io/providers/aliyun/alicloud/latest/docs/resources/ram_account_password_policy
        :param conf: alicloud_ram_account_password_policy configuration
        :return: <CheckResult>
        """

        if conf.get('max_login_attempts'):
            length = force_int(conf.get('max_login_attempts')[0])
            if length is None:
                return CheckResult.UNKNOWN
            if length <= 5:
                return CheckResult.PASSED
            self.evaluated_keys = ["max_login_attempts"]
            return CheckResult.FAILED
        return CheckResult.PASSED


check = PasswordPolicyMaxLogin()

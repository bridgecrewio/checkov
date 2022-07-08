from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class PasswordPolicyMaxAge(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Ram Account Password Policy Max Age less than/equal to 90 days"
        id = "CKV_ALI_24"
        supported_resources = ['alicloud_ram_account_password_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'max_password_age'

    def get_expected_value(self):
        return 90

    def scan_resource_conf(self, conf):
        """
            validates ram password policy
            https://registry.terraform.io/providers/aliyun/alicloud/latest/docs/resources/ram_account_password_policy
        :param conf: alicloud_ram_account_password_policy configuration
        :return: <CheckResult>
        """

        if conf.get('max_password_age') and isinstance(conf.get('max_password_age'), list):
            length = conf.get('max_password_age')[0]
            if 0 < length <= 90:
                return CheckResult.PASSED
        self.evaluated_keys = ["max_password_age"]
        return CheckResult.FAILED


check = PasswordPolicyMaxAge()

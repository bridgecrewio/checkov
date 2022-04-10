from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.util.type_forcers import force_int


class PasswordPolicyLength(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure RAM password policy requires minimum length of 14 or greater"
        id = "CKV_ALI_13"
        supported_resources = ['alicloud_ram_account_password_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'minimum_password_length'

    def get_expected_value(self):
        return 14

    def scan_resource_conf(self, conf):
        """
            validates ram password policy
            https://registry.terraform.io/providers/aliyun/alicloud/latest/docs/resources/ram_account_password_policy
        :param conf: alicloud_ram_account_password_policy configuration
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

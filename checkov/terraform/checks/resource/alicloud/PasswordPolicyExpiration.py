from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.util.type_forcers import force_int


class PasswordPolicyExpiration(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure RAM password policy expires passwords within 90 days or less"
        id = "CKV_ALI_16"
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
        key = 'max_password_age'
        if key in conf.keys():
            max_age = conf[key][0]
            if self._is_variable_dependant(max_age):
                return CheckResult.UNKNOWN
            max_age = force_int(max_age)
            if max_age and 0 < max_age <= 90:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = PasswordPolicyExpiration()

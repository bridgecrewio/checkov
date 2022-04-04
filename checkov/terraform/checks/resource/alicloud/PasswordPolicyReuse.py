from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.util.type_forcers import force_int


class PasswordPolicyReuse(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure RAM password policy prevents password reuse"
        id = "CKV_ALI_18"
        supported_resources = ['alicloud_ram_account_password_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'password_reuse_prevention'

    def get_expected_value(self):
        return 24

    def scan_resource_conf(self, conf):
        """
            validates ram password policy
            https://registry.terraform.io/providers/aliyun/alicloud/latest/docs/resources/ram_account_password_policy
        :param conf: alicloud_ram_account_password_policy configuration
        :return: <CheckResult>
        """
        key = 'password_reuse_prevention'
        if key in conf.keys():
            reuse = conf[key][0]
            if self._is_variable_dependant(reuse):
                return CheckResult.UNKNOWN
            reuse = force_int(reuse)
            if not (reuse and reuse < 24):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = PasswordPolicyReuse()

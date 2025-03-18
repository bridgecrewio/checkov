from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class TwoFASignOnPolicyRule(BaseResourceCheck):
    def __init__(self):
        name = "Ensure 2FA is enabled for an Okta application signon policy rule"
        id = "CKV_OKTA_1"
        supported_resources = ["okta_app_signon_policy_rule"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if "factor_mode" in conf:
            factor_mode = conf["factor_mode"][0]
            if factor_mode == "1FA":
                return CheckResult.FAILED

        return CheckResult.PASSED


check = TwoFASignOnPolicyRule()

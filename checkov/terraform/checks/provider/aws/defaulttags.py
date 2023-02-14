
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.provider.base_check import BaseProviderCheck


class DefaultTags(BaseProviderCheck):
    def __init__(self) -> None:
        name = "Ensure provider defines default tags"
        id = "CKV_AWS_297"
        supported_provider = ["aws"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_provider=supported_provider)

    def scan_provider_conf(self, conf) :
        if conf.get("default_tags"):
            return CheckResult.PASSED
        return CheckResult.FAILED


check = DefaultTags()

import re
from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.provider.base_check import BaseProviderCheck


class AWSDefaultTags(BaseProviderCheck):
    def __init__(self) -> None:
        name = "Ensure AWS provider uses default_tags"
        id = "CKV_AWS_166"
        supported_provider = ["aws"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_provider=supported_provider)

    def scan_provider_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """
            AWS provider should specify default tags:
            https://registry.terraform.io/providers/hashicorp/aws/latest/docs#default_tags
        :param conf: aws provider configuration
        :return: <CheckResult>
        """
        if "default_tags" in conf.keys():
            default_tags = conf['default_tags'][0]
            if 'tags' in default_tags:
                tags = default_tags['tags'][0]
                if tags:
                    return CheckResult.PASSED
        return CheckResult.FAILED



check = AWSDefaultTags()

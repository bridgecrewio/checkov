from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.provider.base_check import BaseProviderCheck


class AWSDefaultTags(BaseProviderCheck):
    def __init__(self) -> None:
        name = "Ensure AWS provider uses default_tags"
        id = "CKV_AWS_173"
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
        default_tags = conf.get('default_tags')
        if default_tags:
        	tags = default_tags[0].get('tags')
        	if tags and tags[0]:
        		return CheckResult.PASSED
        return CheckResult.FAILED

check = AWSDefaultTags()

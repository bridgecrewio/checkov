from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import List


class AutoScalingTagging(BaseResourceCheck):
    def __init__(self):
        name = "Autoscaling groups should supply tags to launch configurations"
        id = "CKV_AWS_153"
        supported_resources = ['aws_autoscaling_group']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for tag or tags
        """
        if "tag" in conf.keys() or "tags" in conf.keys():
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['tag', 'tags']


check = AutoScalingTagging()

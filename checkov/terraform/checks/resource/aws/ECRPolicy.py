import json

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import is_json
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ECRPolicy(BaseResourceCheck):
    def __init__(self):
        name = "Ensure ECR policy is not set to public"
        id = "CKV_AWS_32"
        supported_resources = ['aws_ecr_repository_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for public * policy for ecr repository:
            https://www.terraform.io/docs/providers/aws/r/ecr_repository_policy.html
        :param conf: aws_ecr_repository configuration
        :return: <CheckResult>
        """
        if "policy" in conf.keys():
            if is_json(conf["policy"][0]):
                if json.loads(conf["policy"][0])['Statement'][0]['Principal'] == '*':
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = ECRPolicy()

from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class PublicResourceBasedPolicy(BaseResourceCheck):
    def __init__(self):
        name = "Ensure resource-based policies don't allow public actions on resource"
        id = "CKV_AWS_283"
        supported_resources = ('aws_sns_topic_policy', 'aws_sqs_queue_policy', 'aws_s3_bucket_policy')
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, supported_resources=supported_resources, categories=categories)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if conf.get('policy'):
            policy = conf['policy'][0]
            statements = force_list(policy.get('Statement'))
            for statement in statements:
                if statement.get('Effect', 'Allow') == 'Allow' and statement.get('Action') and \
                        statement.get('Principal') and not statement.get('Condition'):
                    principal = statement['Principal']
                    if principal == '*' or isinstance(principal, dict) and principal.get('AWS') == '*':
                        return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.PASSED


check = PublicResourceBasedPolicy()

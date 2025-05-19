from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import List


class SQSOverlyPermissive(BaseResourceCheck):
    def __init__(self):
        name = "Ensure SQS policy does not allow public access through wildcards"
        id = "CKV_AWS_387"
        supported_resources = ['aws_sqs_queue_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "policy" in conf.keys():
            policy = conf["policy"][0]
            if isinstance(policy, dict):
                for statement in policy.get('Statement', []):
                    if isinstance(statement, dict):
                        # Check Effect is Allow
                        if statement.get('Effect') != 'Allow':
                            continue

                        # Check Action starts with sqs: or SQS:
                        action = statement.get('Action', '')
                        if isinstance(action, str):
                            actions = [action]
                        else:
                            actions = action

                        has_sqs_action = any(
                            isinstance(a, str) and (a == '*' or a.startswith('sqs:') or a.startswith('SQS:')) for a in actions)
                        if not has_sqs_action:
                            continue

                        # Check Principal
                        principal = statement.get('Principal', {})
                        if isinstance(principal, str) and principal == '*':
                            if 'Condition' not in statement:
                                return CheckResult.FAILED
                        elif isinstance(principal, dict) and 'AWS' in principal:
                            aws_principal = principal['AWS']
                            if isinstance(aws_principal, str) and aws_principal == '*':
                                if 'Condition' not in statement:
                                    return CheckResult.FAILED
                            elif isinstance(aws_principal, list) and '*' in aws_principal:
                                if 'Condition' not in statement:
                                    return CheckResult.FAILED

        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['policy']


check = SQSOverlyPermissive()

from policyuniverse.policy import Policy

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SQSQueuePolicyAnyPrincipal(BaseResourceCheck):

    def __init__(self):
        name = "Ensure SQS queue policy is not public by only allowing specific services or principals to access it"
        id = "CKV_AWS_168"
        supported_resources = ['aws_sqs_queue_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        conf_policy = conf.get("policy")
        if conf_policy:
            if isinstance(conf_policy[0], dict):
                policy = Policy(conf_policy[0])
                if policy.is_internet_accessible():
                    return CheckResult.FAILED
            else:
                return CheckResult.UNKNOWN

        return CheckResult.PASSED

check = SQSQueuePolicyAnyPrincipal()



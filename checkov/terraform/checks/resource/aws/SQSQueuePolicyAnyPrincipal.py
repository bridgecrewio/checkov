from __future__ import annotations

from typing import Any

from cloudsplaining.scan.resource_policy_document import ResourcePolicyDocument

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SQSQueuePolicyAnyPrincipal(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure SQS queue policy is not public by only allowing specific services or principals to access it"
        id = "CKV_AWS_168"
        supported_resources = ("aws_sqs_queue_policy", "aws_sqs_queue")
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        conf_policy = conf.get("policy")
        if conf_policy:
            if isinstance(conf_policy[0], dict):
                try:
                    policy = ResourcePolicyDocument(policy=conf_policy[0])
                    if policy.internet_accessible_actions:
                        return CheckResult.FAILED
                except (TypeError, AttributeError):
                    return CheckResult.UNKNOWN
            else:
                return CheckResult.UNKNOWN

        return CheckResult.PASSED

    def get_evaluated_keys(self) -> list[str]:
        return ["policy"]


check = SQSQueuePolicyAnyPrincipal()

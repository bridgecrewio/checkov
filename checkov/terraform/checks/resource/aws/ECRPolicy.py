from __future__ import annotations

from typing import Any

from cloudsplaining.scan.resource_policy_document import ResourcePolicyDocument

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ECRPolicy(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure ECR policy is not set to public"
        id = "CKV_AWS_32"
        supported_resources = ("aws_ecr_repository_policy",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        conf_policy = conf.get("policy")
        if conf_policy and conf_policy[0]:
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


check = ECRPolicy()

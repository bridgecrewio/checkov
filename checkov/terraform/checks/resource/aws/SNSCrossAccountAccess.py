from __future__ import annotations

from typing import Any

from cloudsplaining.scan.resource_policy_document import ResourcePolicyDocument

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SNSCrossAccountAccess(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure AWS SNS topic policies do not allow cross-account access"
        id = "CKV_AWS_385"
        supported_resources = ("aws_sns_topic_policy",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        conf_policy = conf.get("policy")

        if not conf_policy:
            return CheckResult.PASSED

        if conf_policy:
            if isinstance(conf_policy[0], dict):
                for policy in conf_policy:
                    try:
                        processed_policy = ResourcePolicyDocument(policy=policy)
                        for statement in processed_policy.statements:
                            if statement.effect != "Allow":
                                continue

                            has_specific_aws_iam_arn_principal = False

                            aws_principal_values = []
                            if statement.statement and "Principal" in statement.statement and "AWS" in statement.statement["Principal"]:
                                raw_aws_principals = statement.statement["Principal"]["AWS"]
                                if isinstance(raw_aws_principals, str):
                                    aws_principal_values.append(raw_aws_principals)
                                elif isinstance(raw_aws_principals, list):
                                    aws_principal_values.extend(raw_aws_principals)

                            for principal_str in aws_principal_values:
                                if isinstance(principal_str, str) and \
                                        principal_str.startswith("arn:aws:iam::") and \
                                        principal_str != "*":
                                    has_specific_aws_iam_arn_principal = True
                                    break

                            if has_specific_aws_iam_arn_principal:
                                if not statement.conditions:
                                    return CheckResult.FAILED

                    except (TypeError, AttributeError):
                        return CheckResult.UNKNOWN
            else:
                return CheckResult.UNKNOWN
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> list[str]:
        return ["policy"]


check = SNSCrossAccountAccess()

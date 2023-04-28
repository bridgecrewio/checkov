from __future__ import annotations

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list, extract_policy_dict
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import Any


class IAMStarResourcePolicyDocument(BaseResourceCheck):
    def __init__(self) -> None:
        name = 'Ensure no IAM policies documents allow "*" as a statement\'s resource'
        id = "CKV_AWS_355"
        supported_resources = (
            "aws_iam_role_policy",
            "aws_iam_user_policy",
            "aws_iam_group_policy",
            "aws_iam_policy",
            "aws_ssoadmin_permission_set_inline_policy",
        )
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        policy_block = None
        if "policy" in conf.keys():
            policy_block = extract_policy_dict(conf["policy"][0])
        elif "inline_policy" in conf.keys():
            policy_block = extract_policy_dict(conf["inline_policy"][0])
        if policy_block and "Statement" in policy_block.keys():
            for statement in force_list(policy_block["Statement"]):
                if "Resource" in statement:
                    resources = force_list(statement["Resource"])
                    if (
                        isinstance(resources[0], str)
                        and statement.get("Effect", "Allow") == "Allow"
                        and "*" in resources
                    ):
                        # scanning a HCL file
                        return CheckResult.FAILED
                    elif (
                        isinstance(resources[0], list)
                        and statement.get("Effect", ["Allow"]) == ["Allow"]
                        and "*" in resources[0]
                    ):
                        # scanning a TF plan file
                        return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> list[str]:
        return ["policy", "inline_policy"]


check = IAMStarResourcePolicyDocument()

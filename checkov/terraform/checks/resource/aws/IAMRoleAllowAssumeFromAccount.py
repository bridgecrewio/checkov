from __future__ import annotations

import re

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import extract_policy_dict
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import Any

ACCOUNT_ACCESS = re.compile(r"\d{12}|arn:aws:iam::\d{12}:root")


class IAMRoleAllowAssumeFromAccount(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure AWS IAM policy does not allow assume role permission across all services"
        id = "CKV_AWS_61"
        supported_resources = ("aws_iam_role",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        try:
            assume_role_block = extract_policy_dict(conf["assume_role_policy"][0])
            if assume_role_block and "Statement" in assume_role_block:
                for statement in assume_role_block["Statement"]:
                    if statement.get("Effect") == "Deny":
                        continue
                    if "Principal" in statement and "AWS" in statement["Principal"]:
                        # Can be a string or an array of strings
                        aws_principals = statement["Principal"]["AWS"]
                        if isinstance(aws_principals, str) and re.match(ACCOUNT_ACCESS, aws_principals):
                            return CheckResult.FAILED
                        elif isinstance(aws_principals, list):
                            for aws_principal in aws_principals:
                                if isinstance(aws_principal, str) and re.match(ACCOUNT_ACCESS, aws_principal):
                                    return CheckResult.FAILED
        except Exception:  # nosec
            return CheckResult.UNKNOWN

        return CheckResult.PASSED

    def get_evaluated_keys(self) -> list[str]:
        return ["assume_role_policy"]


check = IAMRoleAllowAssumeFromAccount()

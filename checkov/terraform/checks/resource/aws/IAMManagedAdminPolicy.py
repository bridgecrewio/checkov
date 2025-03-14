from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


ADMIN_POLICY_NAME = "AdministratorAccess"
ADMIN_POLICY_ARN = f"arn:aws:iam::aws:policy/{ADMIN_POLICY_NAME}"


class IAMManagedAdminPolicy(BaseResourceCheck):
    def __init__(self) -> None:
        # This is the full description of your check
        description = "Disallow IAM roles, users, and groups from using the AWS AdministratorAccess policy"

        # This is the Unique ID for your check
        id = "CKV_AWS_274"

        # These are the terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = (
            "aws_iam_role",
            "aws_iam_policy_attachment",
            "aws_iam_role_policy_attachment",
            "aws_iam_user_policy_attachment",
            "aws_iam_group_policy_attachment",
            "aws_ssoadmin_managed_policy_attachment",
        )

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = (CheckCategories.IAM,)
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if self.entity_type == "aws_iam_role":
            if "managed_policy_arns" in conf.keys():
                if ADMIN_POLICY_ARN in conf["managed_policy_arns"][0]:
                    self.evaluated_keys = ["managed_policy_arns"]
                    return CheckResult.FAILED

        elif self.entity_type in (
            "aws_iam_policy_attachment",
            "aws_iam_role_policy_attachment",
            "aws_iam_user_policy_attachment",
            "aws_iam_group_policy_attachment",
        ):
            policy_arn = conf.get("policy_arn")
            if policy_arn and isinstance(policy_arn, list) and policy_arn[0] == ADMIN_POLICY_ARN:
                self.evaluated_keys = ["policy_arn"]
                return CheckResult.FAILED

        elif self.entity_type in (
            "aws_ssoadmin_managed_policy_attachment"
        ):
            managed_policy_arn = conf.get("managed_policy_arn")
            if managed_policy_arn and isinstance(managed_policy_arn, list) and managed_policy_arn[0] == ADMIN_POLICY_ARN:
                self.evaluated_keys = ["managed_policy_arn"]
                return CheckResult.FAILED

        return CheckResult.PASSED


check = IAMManagedAdminPolicy()

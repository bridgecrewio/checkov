from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.data.base_check import BaseDataCheck


ADMIN_POLICY_NAME = "AdministratorAccess"
ADMIN_POLICY_ARN = f"arn:aws:iam::aws:policy/{ADMIN_POLICY_NAME}"


class IAMManagedAdminPolicy(BaseDataCheck):
    def __init__(self):
        # This is the full description of your check
        description = "Disallow policies from using the AWS AdministratorAccess policy"

        # This is the Unique ID for your check
        id = "CKV_AWS_275"

        # These are the terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_data = ("aws_iam_policy",)

        # Valid CheckCategories checkov/common/models/enums.py
        categories = (CheckCategories.IAM,)
        super().__init__(name=description, id=id, categories=categories, supported_data=supported_data)

    def scan_data_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if "name" in conf.keys():
            if conf.get("name")[0] == ADMIN_POLICY_NAME:
                return CheckResult.FAILED

        if "arn" in conf.keys():
            if conf.get("arn")[0] == ADMIN_POLICY_ARN:
                return CheckResult.FAILED

        return CheckResult.PASSED


check = IAMManagedAdminPolicy()

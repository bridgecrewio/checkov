from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class IAMPasswordLength(BaseResourceCheck):
    def __init__(self) -> None:
        name = "OCI IAM password policy for local (non-federated) users has a minimum length of 14 characters"
        id = "CKV_OCI_18"
        supported_resources = ('oci_identity_authentication_policy',)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if 'password_policy' in conf.keys():
            self.evaluated_keys = ["password_policy"]
            rules = conf.get("password_policy")[0]
            if 'minimum_password_length' in rules:
                password_length = rules.get("minimum_password_length")
                if isinstance(password_length[0], int) and password_length[0] < 14:
                    self.evaluated_keys = ["password_policy/minimum_password_length"]
                    return CheckResult.FAILED
                return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.FAILED


check = IAMPasswordLength()

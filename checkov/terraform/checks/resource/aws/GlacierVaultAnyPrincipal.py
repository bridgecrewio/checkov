from __future__ import annotations

import json
import re
from typing import List, Any

from cloudsplaining.scan.resource_policy_document import ResourcePolicyDocument

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

DATA_TO_JSON_PATTERN = re.compile(r"\$?\{?(.+?)(?=.json).json\}?")


class GlacierVaultAnyPrincipal(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Glacier Vault access policy is not public by only allowing specific services or principals to access it"
        id = "CKV_AWS_167"
        supported_resources = ("aws_glacier_vault",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if "access_policy" not in conf:
            return CheckResult.PASSED
        policy_obj = conf["access_policy"][0]
        if isinstance(policy_obj, str):
            if re.match(DATA_TO_JSON_PATTERN, policy_obj):
                return CheckResult.UNKNOWN
            else:
                try:
                    policy_obj = json.loads(policy_obj)
                except Exception:
                    return CheckResult.UNKNOWN
        try:
            policy = ResourcePolicyDocument(policy=policy_obj)
            if policy.internet_accessible_actions:
                return CheckResult.FAILED
        except (TypeError, AttributeError):
            return CheckResult.UNKNOWN
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ["access_policy"]


check = GlacierVaultAnyPrincipal()

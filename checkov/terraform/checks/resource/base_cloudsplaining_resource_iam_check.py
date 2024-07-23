from __future__ import annotations

from abc import ABC
from typing import Dict, List, Any

from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.checks.utils.base_cloudsplaining_iam_scanner import BaseTerraformCloudsplainingIAMScanner


class BaseTerraformCloudsplainingResourceIAMCheck(BaseResourceCheck, BaseTerraformCloudsplainingIAMScanner, ABC):
    def __init__(self, name: str, id: str) -> None:
        supported_resources = (
            "aws_iam_role_policy",
            "aws_iam_user_policy",
            "aws_iam_group_policy",
            "aws_iam_policy",
            "aws_ssoadmin_permission_set_inline_policy",
        )
        super().__init__(name=name, id=id, categories=(CheckCategories.IAM,), supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        return self.scan_conf(conf)

    @property
    def cache_key(self) -> str:
        return self.entity_path

    def should_scan_conf(self, conf: Dict[str, List[Any]]) -> bool:
        if self.entity_type == "aws_ssoadmin_permission_set_inline_policy":
            return "inline_policy" in conf

        return "policy" in conf

    def convert_to_iam_policy(self, conf: Dict[str, Any]) -> PolicyDocument:
        if self.entity_type == "aws_ssoadmin_permission_set_inline_policy":
            policy: dict[str, Any] = conf['inline_policy'][0]
        else:
            policy = conf['policy'][0]

        return PolicyDocument(policy)

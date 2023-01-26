from abc import ABC
from typing import Dict, List, Any

from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_cloudsplaining_resource_iam_scanner import \
    BaseCloudsplainingResourceIAMScanner
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class BaseCloudsplaininResourceIAMCheck(BaseResourceCheck, BaseCloudsplainingResourceIAMScanner, ABC):
    def __init__(self, name: str, id: str) -> None:
        super().__init__(name=name, id=id, categories=[CheckCategories.IAM], supported_resources=["aws_iam_policy"])

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        return self.scan_conf(conf)

    @property
    def cache_key(self) -> str:
        return self.entity_path

    def should_scan_conf(self, conf: Dict[str, List[Any]]) -> bool:
        return "policy" in conf.keys()

    def convert_to_iam_policy(self, conf: Dict[str, Any]) -> PolicyDocument:
        policy = conf['policy']  # type: Dict[str, Any]
        return PolicyDocument(policy)

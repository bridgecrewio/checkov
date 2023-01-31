from abc import ABC
from typing import Dict, List, Any

from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.data.base_check import BaseDataCheck
from checkov.terraform.checks.utils.base_cloudsplaining_iam_scanner import BaseTerraformCloudsplainingIAMScanner
from checkov.terraform.checks.utils.iam_terraform_document_to_policy_converter import (
    convert_terraform_conf_to_iam_policy,
)


class BaseTerraformCloudsplainingDataIAMCheck(BaseDataCheck, BaseTerraformCloudsplainingIAMScanner, ABC):
    def __init__(self, name: str, id: str) -> None:
        super().__init__(name=name, id=id, categories=[CheckCategories.IAM], supported_data=["aws_iam_policy_document"])

    def scan_data_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        return self.scan_conf(conf)

    @property
    def cache_key(self) -> str:
        return self.entity_path

    def should_scan_conf(self, conf: Dict[str, List[Any]]) -> bool:
        return "statement" in conf.keys()

    def convert_to_iam_policy(self, conf: Dict[str, List[Any]]) -> PolicyDocument:
        converted_conf = convert_terraform_conf_to_iam_policy(conf)
        return PolicyDocument(converted_conf)

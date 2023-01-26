from abc import ABC
from typing import Dict, List, Any

from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.terraform.checks.utils.base_cloudsplaining_iam_check import BaseCloudsplainingIAMScanner
from checkov.terraform.checks.utils.iam_terraform_document_to_policy_converter import \
    convert_terraform_conf_to_iam_policy


class BaseCloudsplainingDataIAMScanner(BaseCloudsplainingIAMScanner, ABC):
    def should_scan_conf(self, conf: Dict[str, List[Any]]) -> bool:
        return "statement" in conf.keys()

    def convert_to_iam_policy(self, conf: Dict[str, List[Any]]) -> PolicyDocument:
        converted_conf = convert_terraform_conf_to_iam_policy(conf)
        return PolicyDocument(converted_conf)


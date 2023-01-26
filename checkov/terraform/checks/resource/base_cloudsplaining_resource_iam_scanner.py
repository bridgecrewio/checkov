from abc import ABC
from typing import Dict, List, Any

from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.terraform.checks.utils.base_cloudsplaining_iam_check import BaseCloudsplainingIAMScanner


class BaseCloudsplainingResourceIAMScanner(BaseCloudsplainingIAMScanner, ABC):
    def should_scan_conf(self, conf: Dict[str, List[Any]]) -> bool:
        return "policy" in conf.keys()

    def convert_to_iam_policy(self, conf: Dict[str, Any]) -> PolicyDocument:
        policy = conf['policy']  # type: Dict[str, Any]
        return PolicyDocument(policy)

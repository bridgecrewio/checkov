import json
import logging
from abc import abstractmethod
from typing import Dict, List, Any, Union

from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.data.base_check import BaseDataCheck
from checkov.terraform.checks.utils.iam_terraform_document_to_policy_converter import (
    convert_terraform_conf_to_iam_policy,
)


class BaseCloudsplainingIAMCheck(BaseDataCheck):
    # creating a PolicyDocument is computational expensive,
    # therefore a cache is defined at class level
    policy_document_cache: Dict[str, PolicyDocument] = {}

    def __init__(self, name: str, id: str) -> None:
        super().__init__(name=name, id=id, categories=[CheckCategories.IAM], supported_data=["aws_iam_policy_document"])

    def scan_data_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if "statement" in conf.keys():
            try:
                if self.entity_path not in BaseCloudsplainingIAMCheck.policy_document_cache.keys():
                    converted_conf = convert_terraform_conf_to_iam_policy(conf)
                    policy = PolicyDocument(converted_conf)
                    BaseCloudsplainingIAMCheck.policy_document_cache[self.entity_path] = policy
                violations = self.cloudsplaining_analysis(
                    BaseCloudsplainingIAMCheck.policy_document_cache[self.entity_path]
                )
            except Exception:
                # this might occur with templated iam policies where ARN is not in place or similar
                logging.debug(f"could not run cloudsplaining analysis on policy {conf}")
                return CheckResult.UNKNOWN
            if violations:
                logging.debug(f"detailed cloudsplainging finding: {json.dumps(violations, indent=2, default=str)}")
                return CheckResult.FAILED
        return CheckResult.PASSED

    @abstractmethod
    def cloudsplaining_analysis(self, policy: PolicyDocument) -> Union[List[str], List[Dict[str, Any]]]:
        raise NotImplementedError()

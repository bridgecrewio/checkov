import fnmatch
import logging
from abc import ABC
from typing import Dict, List, Any, Union

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

    def cloudsplaining_enrich_evaluated_keys(self, policy: PolicyDocument,
                                             violating_actions: Union[List[str], List[Dict[str, Any]]]) -> None:
        try:
            # in case we have violating actions for this policy we start looking for it through the statements
            for stmt_idx, statement in enumerate(policy.statements):
                actions = statement.statement.get('Action')  # get the actions for this statement
                if actions:
                    if isinstance(actions, str):
                        for violating_action in violating_actions:
                            if fnmatch.fnmatch(violating_action.lower(), actions.lower()):  # found the violating action in our list of actions
                                self.evaluated_keys.append(f"statement/[{stmt_idx}]/actions")
                                return
                    if isinstance(actions, list):
                        for action in actions:      # go through the actions of this statement and try to match one violation
                            for violating_action in violating_actions:
                                if isinstance(action, str) and fnmatch.fnmatch(violating_action.lower(), action.lower()):      # found the violating action in our list of actions
                                    self.evaluated_keys.append(f"statement/[{stmt_idx}]/actions")
                                    return
        except Exception as e:
            logging.warning(f'Failed enriching cloudsplaining evaluated keys due to: {e}')

from __future__ import annotations

import fnmatch
import logging
from abc import ABC
from typing import Dict, List, Any, Union

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
                                self.evaluated_keys.append(f"policy/Statement/[{stmt_idx}]/Action")
                                return
                    if isinstance(actions, list):
                        for action in actions:  # go through the actions of this statement and try to match one violation
                            for violating_action in violating_actions:
                                if isinstance(action, str) and fnmatch.fnmatch(violating_action.lower(), action.lower()):  # found the violating action in our list of actions
                                    self.evaluated_keys.append(f"policy/Statement/[{stmt_idx}]/Action")
                                    return
        except Exception as e:
            logging.warning(f'Failed enriching cloudsplaining evaluated keys due to: {e}')

from __future__ import annotations

import fnmatch
import json
import logging
from abc import abstractmethod
from collections import defaultdict
from functools import partial
from typing import Any

from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.utils.iam_cloudformation_document_to_policy_converter import \
    convert_cloudformation_conf_to_iam_policy


class BaseCloudsplainingIAMCheck(BaseResourceCheck):
    # creating a PolicyDocument is computational expensive,
    # therefore a cache is defined at class level
    policy_document_cache: dict[str, dict[str, PolicyDocument]] = defaultdict(partial(defaultdict, PolicyDocument))  # noqa: CCE003

    def __init__(self, name: str, id: str) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=[CheckCategories.IAM],
            supported_resources=[
                "AWS::IAM::Policy",
                "AWS::IAM::ManagedPolicy",
                "AWS::IAM::Group",
                "AWS::IAM::Role",
                "AWS::IAM::User",
            ]
        )

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if conf.get('Properties'):
            props_conf = conf['Properties']
            policies_key = 'Policies'

            # Obtain a list of 1 or more policies regardless of resource schema
            if policies_key in props_conf.keys():
                policy_conf = props_conf[policies_key]
            else:
                policy_conf = [props_conf]

            # Scan all policies
            for policy in policy_conf:
                policy_doc_key = 'PolicyDocument'
                if not isinstance(policy, dict) or policy_doc_key not in policy.keys():
                    continue
                policy_statement = None
                policy_name = policy.get("PolicyName")
                if isinstance(policy_name, str):
                    policy_statement = self.policy_document_cache.get(self.entity_path, {}).get(policy.get("PolicyName"))

                try:
                    if not policy_statement:
                        # When using unresolved Cfn functions, policy is an str
                        policy_doc = policy[policy_doc_key]
                        if not isinstance(policy_doc, dict):
                            return CheckResult.UNKNOWN
                        converted_policy_doc = convert_cloudformation_conf_to_iam_policy(policy_doc)
                        statement_key = 'Statement'
                        if statement_key in converted_policy_doc:
                            policy_statement = PolicyDocument(converted_policy_doc)
                            self.policy_document_cache[self.entity_path][policy.get("PolicyName")] = policy_statement
                    self.cloudsplaining_enrich_evaluated_keys(policy_statement)
                    violations = self.cloudsplaining_analysis(policy_statement)
                    if violations:
                        logging.debug(f"detailed cloudsplaining finding: {json.dumps(violations)}")
                        return CheckResult.FAILED
                except Exception:
                    # this might occur with templated iam policies where ARN is not in place or similar
                    logging.debug(f"could not run cloudsplaining analysis on policy {conf}")
                    return CheckResult.UNKNOWN
            return CheckResult.PASSED

    @abstractmethod
    def cloudsplaining_analysis(self, policy: PolicyDocument) -> list[str]:
        raise NotImplementedError()

    def cloudsplaining_enrich_evaluated_keys(self, policy: PolicyDocument) -> None:
        try:
            violating_actions = self.cloudsplaining_analysis(policy)
            if violating_actions:
                # in case we have violating actions for this policy we start looking for it through the statements
                for stmt_idx, statement in enumerate(policy.statements):
                    actions = statement.statement.get('Action')  # get the actions for this statement
                    if actions:
                        if isinstance(actions, str):
                            for violating_action in violating_actions:
                                if fnmatch.fnmatch(violating_action, actions):  # found the violating action in our list of actions
                                    self.evaluated_keys = [f"Properties/PolicyDocument/Statement/[{stmt_idx}]/Action"]
                                    break
                        if isinstance(actions, list):
                            for action_idx, action in enumerate(actions):      # go through the actions of this statement and try to match one violation
                                for violating_action in violating_actions:
                                    if fnmatch.fnmatch(violating_action, action):      # found the violating action in our list of actions
                                        self.evaluated_keys.append(
                                            f"Properties/PolicyDocument/Statement/[{stmt_idx}]/Action/[{action_idx}]/"
                                        )
                                        break
        except Exception as e:
            logging.warning(f'Failed enriching cloudsplaining evaluated keys due to: {e}')

from __future__ import annotations

import json
import logging
import re
from typing import Any

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.consts import SLS_DEFAULT_VAR_PATTERN
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.parsers.node import StrNode


class ECRPolicy(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure ECR policy is not set to public"
        id = "CKV_AWS_32"
        supported_resources = ("AWS::ECR::Repository",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        """
            Looks for public * policy for ecr repository:
            https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecr-repository.html
        :param conf: aws_ecr_repository configuration
        :return: <CheckResult>
        """
        self.evaluated_keys = ["Properties/RepositoryPolicyText/Statement"]
        properties = conf.get("Properties")
        if not properties or not isinstance(properties, dict):
            return CheckResult.PASSED
        policy_text = properties.get("RepositoryPolicyText")
        if not policy_text:
            return CheckResult.PASSED
        if isinstance(policy_text, str):
            try:
                policy_text = json.loads(str(policy_text))
            except json.decoder.JSONDecodeError as e:
                if re.match(SLS_DEFAULT_VAR_PATTERN, str(policy_text)):
                    # Case where the template is a sub-CFN configuration inside a serverless configuration,
                    # and the policy is a variable expression
                    logging.info(f"Encountered variable expression {str(policy_text)} in resource ${self.entity_path}")
                else:
                    logging.error(
                        f"Malformed policy configuration {str(policy_text)} of resource {self.entity_path}\n{e}"
                    )
                return CheckResult.UNKNOWN
        if "Statement" in policy_text.keys():
            for statement_index, statement in enumerate(policy_text["Statement"]):
                if "Principal" in statement.keys():
                    for principal_index, principal in enumerate(statement["Principal"]):
                        if principal == "*" and not self.check_for_constrained_condition(statement):
                            self.evaluated_keys = [
                                f"Properties/RepositoryPolicyText/Statement/[{statement_index}]/Principal/[{principal_index}]"
                            ]
                            return CheckResult.FAILED
        return CheckResult.PASSED

    def check_for_constrained_condition(self, statement: dict[str, Any]) -> bool:
        """
        Checks to see if there is a constraint on a a wildcarded principal
        :param statement: statement from aws_repository_configuration
        :return: true if there is a constraint
        """
        if "Condition" in statement.keys():
            condition = statement["Condition"]
            if "ForAllValues:StringEquals" in condition.keys():
                if "aws:PrincipalOrgID" in condition["ForAllValues:StringEquals"].keys():
                    return True
        return False


check = ECRPolicy()

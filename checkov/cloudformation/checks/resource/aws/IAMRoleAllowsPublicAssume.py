import json
from typing import Dict, Any

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class IAMRoleAllowsPublicAssume(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure IAM role allows only specific services or principals to assume it"
        id = "CKV_AWS_60"
        supported_resources = ("AWS::IAM::Role",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["Properties/AssumeRolePolicyDocument/Statement"]
        properties = conf.get("Properties")
        if isinstance(properties, dict):
            assume_role_policy_doc = properties.get("AssumeRolePolicyDocument")
            if isinstance(assume_role_policy_doc, str):
                try:
                    assume_role_policy_doc = json.loads(assume_role_policy_doc)
                except Exception:
                    return CheckResult.UNKNOWN
            if isinstance(assume_role_policy_doc, dict) and assume_role_policy_doc.get("Statement"):
                statements = assume_role_policy_doc["Statement"]
                if isinstance(statements, list):
                    for statement_index, statement in enumerate(statements):
                        if not isinstance(statement, dict):
                            continue
                        if statement.get("Effect") == "Deny":
                            continue
                        principal = statement.get("Principal")
                        if isinstance(principal, dict):
                            aws_principals = principal.get("AWS")
                            if aws_principals == "*":
                                self.evaluated_keys = [
                                    f"Properties/AssumeRolePolicyDocument/Statement/[{statement_index}]/Principal/AWS"
                                ]
                                return CheckResult.FAILED
                            if isinstance(aws_principals, list):
                                for principal_index, principal in enumerate(aws_principals):
                                    if principal == "*":
                                        self.evaluated_keys = [
                                            f"Properties/AssumeRolePolicyDocument/Statement/[{statement_index}]/Principal/[{principal_index}]/AWS"
                                        ]
                                        return CheckResult.FAILED
        return CheckResult.PASSED


check = IAMRoleAllowsPublicAssume()

from typing import Dict, List, Any

from checkov.terraform.checks.data.base_check import BaseDataCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class ResourcePolicyDocument(BaseDataCheck):
    def __init__(self) -> None:
        name = 'Ensure IAM policies limit resource access'
        id = "CKV_AWS_356"
        supported_data = ["aws_iam_policy_document"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_data=supported_data)

    def scan_data_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """
            validates iam policy document
            https://learn.hashicorp.com/terraform/aws/iam-policy
        :param conf: aws_kms_key configuration
        :return: <CheckResult>
        """

        for statement in conf.get("statement", []):
            if not isinstance(statement, list):
                statement = [statement]
            for stmt in statement:
                if (
                    isinstance(stmt, dict)
                    and stmt.get("effect", ["Allow"]) == ["Allow"]
                    and stmt.get("resources")
                    and ["*"] == stmt["resources"][0]
                ):
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = ResourcePolicyDocument()

from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.data.base_check import BaseDataCheck


class IAMPublicActionsPolicy(BaseDataCheck):
    def __init__(self):
        name = 'Ensure no IAM policies documents allow ALL or any AWS principal permissions to the resource'
        id = "CKV_AWS_283"
        supported_data = ["aws_iam_policy_document"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_data=supported_data)

    def scan_data_conf(self, conf: Dict[str, List[Any]], entity_type: str) -> CheckResult:
        statements = force_list(conf.get('statement'))
        for statement in statements:
            if isinstance(statement, dict):
                if not statement.get('condition'):
                    principals = force_list(statement.get('principals'))
                    for principal in principals:
                        if isinstance(principal, dict):
                            principal_type = principal.get('type', [''])[0]
                            principal_identifiers = principal.get('identifiers', [])
                            if principal_type == 'AWS' and principal_identifiers and isinstance(principal_identifiers[0], list) and '*' in principal_identifiers[0]:
                                return CheckResult.FAILED

        return CheckResult.PASSED


check = IAMPublicActionsPolicy()

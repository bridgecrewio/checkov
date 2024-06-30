from typing import Dict, List, Any
import re
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.data.base_check import BaseDataCheck

gh_repo_regex = re.compile(r'repo:[^/]+/[^/]+')


class GithubActionsOIDCTrustPolicy(BaseDataCheck):
    def __init__(self):
        name = 'Ensure GitHub Actions OIDC trust policies only allows actions from a specific known organization'
        id = "CKV_AWS_358"
        supported_data = ("aws_iam_policy_document",)
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_data=supported_data)

    def scan_data_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        statements = force_list(conf.get('statement'))
        for statement in statements:
            found_federated_gh_oidc = False
            if isinstance(statement, dict):
                if statement.get('principals'):
                    principals = statement['principals']
                    for principal in force_list(principals):
                        if 'type' not in principal and 'identifiers' not in principal:
                            continue
                        principal_type = principal['type']
                        principal_identifiers = principal['identifiers']
                        if isinstance(principal_type, list) and len(
                                principal_type) and 'Federated' in principal_type and isinstance(principal_identifiers,
                                                                                                 list):
                            for identifier in principal_identifiers:
                                if isinstance(identifier,
                                              list) and identifier[0] is not None and \
                                        'oidc-provider/token.actions.githubusercontent.com' in identifier[0]:
                                    found_federated_gh_oidc = True
                                    break
                if not found_federated_gh_oidc:
                    return CheckResult.PASSED
                if found_federated_gh_oidc and not statement.get('condition'):
                    return CheckResult.FAILED
                found_sub_condition_variable = False
                found_sub_condition_value = False
                for condition in statement.get('condition'):
                    condition_variables = condition.get('variable')
                    condition_values = condition.get('values')
                    if isinstance(condition_variables, list):
                        for condition_variable in condition_variables:
                            if condition_variable == 'token.actions.githubusercontent.com:sub':
                                found_sub_condition_variable = True
                                break
                        for condition_value in condition_values:
                            if isinstance(condition_value, list) and gh_repo_regex.search(condition_value[0]):
                                found_sub_condition_value = True
                                break
                        if found_sub_condition_value and found_sub_condition_variable:
                            return CheckResult.PASSED

                # Found a federated GitHub user, but no restrictions
                return CheckResult.FAILED

        return CheckResult.PASSED


check = GithubActionsOIDCTrustPolicy()

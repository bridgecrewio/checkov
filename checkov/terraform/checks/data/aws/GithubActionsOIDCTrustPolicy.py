from typing import Dict, List, Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.data.base_check import BaseDataCheck
from checkov.common.util.oidc_utils import gh_abusable_claims, gh_repo_regex


class GithubActionsOIDCTrustPolicy(BaseDataCheck):
    def __init__(self):
        name = "Ensure AWS GitHub Actions OIDC authorization policies only allow safe claims and claim order"
        id = "CKV_AWS_358"
        supported_data = ("aws_iam_policy_document",)
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_data=supported_data)

    def scan_data_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        statements = force_list(conf.get("statement"))
        for statement in statements:
            found_federated_gh_oidc = False
            if isinstance(statement, dict):
                if statement.get("principals"):
                    principals = statement["principals"]
                    for principal in force_list(principals):
                        if "type" not in principal and "identifiers" not in principal:
                            continue
                        principal_type = principal["type"]
                        principal_identifiers = principal["identifiers"]
                        if (
                            isinstance(principal_type, list)
                            and len(principal_type)
                            and "Federated" in principal_type
                            and isinstance(principal_identifiers, list)
                        ):
                            for identifier in principal_identifiers:
                                if (
                                    isinstance(identifier, list)
                                    and len(identifier) > 0
                                    and identifier[0] is not None
                                    and "oidc-provider/token.actions.githubusercontent.com" in identifier[0]
                                ):
                                    found_federated_gh_oidc = True
                                    break
                if not found_federated_gh_oidc:
                    return CheckResult.PASSED

                # By now we know that the statement is a federated GitHub OIDC provider
                # First check - if the statement is a federated GitHub OIDC provider, it MUST have a condition
                if found_federated_gh_oidc and not statement.get("condition"):
                    return CheckResult.FAILED
                found_sub_condition_variable = False
                found_sub_condition_value = False

                # It is common to have multiple conditions, so we need to iterate over them
                for condition in statement.get("condition"):
                    condition_variables = condition.get("variable")
                    condition_values = condition.get("values")
                    if isinstance(condition_variables, list):
                        for condition_variable in condition_variables:
                            if condition_variable == "token.actions.githubusercontent.com:sub":
                                found_sub_condition_variable = True
                                break

                        # If we didn't find the sub condition variable, we can skip the rest of the checks
                        if not found_sub_condition_variable:
                            continue
                        if isinstance(condition_values, list):
                            for condition_value in condition_values:
                                if isinstance(condition_value, list):
                                    # First -> check if the value is a mere wildcard. If so, it's a fail
                                    # This covers the case where the condition is ['sub':'*']
                                    if len(condition_value) == 1 and condition_value[0] == "*":
                                        return CheckResult.FAILED
                                    # Split the claims by ':' for deeper inspection
                                    split_claims = condition_value[0].split(":")
                                    # The assertion MUST be of the form ['{claim_name_1}:{claim_value_1}:{claim_name_2}:{claim_value_2}...']
                                    # If the length of the split claims is 1, it means that the assertion is ['sub':'{claim_name}'] - this is a fail
                                    if len(split_claims) == 1:
                                        return CheckResult.FAILED
                                    # Second -> Check if the value is a wildcard assertion
                                    # This covers the case where the condition is ['sub':'{claim_name}:*']
                                    if split_claims[1] == "*":
                                        return CheckResult.FAILED
                                    # Third -> Check if the value is an abusable claim
                                    # This covers the case where the condition is ['sub':'{abusable_claim}:{any_value}']
                                    for abusable_claim in gh_abusable_claims:
                                        if split_claims[0].startswith(abusable_claim):
                                            return CheckResult.FAILED
                                    # Fourth -> Check if the value is a repo:org/* -> this is a pass with a warning
                                    if split_claims[0] == "repo" and not gh_repo_regex.match(split_claims[1]):
                                        return CheckResult.FAILED
                                    found_sub_condition_value = True
                                    break
                        if found_sub_condition_value and found_sub_condition_variable:
                            return CheckResult.PASSED

                # Found a federated GitHub user, but no restrictions
                return CheckResult.FAILED

        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ["statement/condition/variable", "statement/condition/values"]


check = GithubActionsOIDCTrustPolicy()

from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.oidc_utils import gh_abusable_claims, gh_repo_regex, gh_sub_condition
from checkov.common.util.type_forcers import extract_policy_dict, force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GithubActionsOIDCTrustPolicyOnRole(BaseResourceCheck):
    """
    Resource-level mirror of CKV_AWS_358 (GithubActionsOIDCTrustPolicy).

    CKV_AWS_358 only inspects `data "aws_iam_policy_document"` blocks. This
    check applies the SAME unsafe-claim logic to `aws_iam_role` resources
    that define their trust policy inline via `assume_role_policy`.

    Logic is intentionally identical to CKV_AWS_358; only the parsing layer
    differs (JSON statement objects vs. HCL `statement{}` blocks). Shared
    constants (gh_sub_condition, gh_abusable_claims, gh_repo_regex) come
    from checkov.common.util.oidc_utils.
    """

    GH_OIDC_PROVIDER_SUBSTR = "oidc-provider/token.actions.githubusercontent.com"

    def __init__(self) -> None:
        name = (
            "Ensure AWS GitHub Actions OIDC authorization policies only allow "
            "safe claims and claim order on IAM role"
        )
        id = "CKV_AWS_393"
        supported_resources = ("aws_iam_role",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if not conf.get("assume_role_policy"):
            return CheckResult.PASSED

        try:
            policy = extract_policy_dict(conf["assume_role_policy"][0])
        except Exception:  # nosec
            return CheckResult.PASSED

        if not policy or "Statement" not in policy:
            return CheckResult.PASSED

        for statement in force_list(policy["Statement"]):
            if not isinstance(statement, dict):
                continue

            if not self._has_github_oidc_federated_principal(statement):
                # No GH-OIDC federated principal in this statement -> not our concern.
                # (Matches CKV_AWS_358 behavior: "if not found_federated_gh_oidc: return PASSED")
                return CheckResult.PASSED

            # Federated GH-OIDC principal MUST come with a Condition.
            condition = statement.get("Condition")
            if not condition or not isinstance(condition, dict):
                return CheckResult.FAILED

            verdict = self._evaluate_sub_conditions(condition)
            if verdict is not None:
                return verdict

            # Federated GH-OIDC principal present, conditions present, but none
            # contained a recognized `:sub` constraint -> unsafe.
            return CheckResult.FAILED

        return CheckResult.PASSED

    def _has_github_oidc_federated_principal(self, statement: dict[str, Any]) -> bool:
        principal = statement.get("Principal")
        if not isinstance(principal, dict):
            return False
        federated = principal.get("Federated")
        if federated is None:
            return False
        for identifier in force_list(federated):
            if isinstance(identifier, str) and self.GH_OIDC_PROVIDER_SUBSTR in identifier:
                return True
        return False

    def _evaluate_sub_conditions(self, condition: dict[str, Any]) -> CheckResult | None:
        """
        Walk Condition operators looking for the `:sub` claim constraint.

        Mirrors CKV_AWS_358's inner loop: returns FAILED on the first unsafe
        value found, PASSED on the first safe value found, or None if no
        `:sub` claim constraint exists in any operator (the caller then
        returns FAILED, matching the data check's "Found a federated GitHub
        user, but no restrictions" path).
        """
        for operator_values in condition.values():
            if not isinstance(operator_values, dict):
                continue
            for variable_name, values in operator_values.items():
                if not isinstance(variable_name, str) or not gh_sub_condition.match(variable_name):
                    continue
                for value in force_list(values):
                    if not isinstance(value, str):
                        continue
                    verdict = self._classify_sub_value(value)
                    if verdict is not None:
                        return verdict
        return None

    @staticmethod
    def _classify_sub_value(value: str) -> CheckResult | None:
        """
        Same four unsafe-pattern checks as CKV_AWS_358, in the same order.
        Returns FAILED for an unsafe value, PASSED for a safe value, or
        None if the value is malformed in a way the data check would also
        skip (defensive; should not normally occur for string values).
        """
        # 1. Bare wildcard: "sub": "*"
        if value == "*":
            return CheckResult.FAILED

        split_claims = value.split(":")

        # 2. Bare claim name with no value: "sub": "invalid"
        if len(split_claims) == 1:
            return CheckResult.FAILED

        # 3. Wildcard assertion on the first claim's value: "sub": "claim:*"
        if split_claims[1] == "*":
            return CheckResult.FAILED

        # 4. Abusable first claim: "sub": "workflow:..." / "environment:..." / etc.
        for abusable_claim in gh_abusable_claims:
            if split_claims[0].startswith(abusable_claim):
                return CheckResult.FAILED

        # 5. "repo:" prefix must be followed by an org/repo-shaped value.
        #    "repo:myOrg*" -> FAIL ; "repo:myOrg/*" -> PASS (per gh_repo_regex)
        if split_claims[0] == "repo" and not gh_repo_regex.match(split_claims[1]):
            return CheckResult.FAILED

        return CheckResult.PASSED

    def get_evaluated_keys(self) -> list[str]:
        return ["assume_role_policy"]


check = GithubActionsOIDCTrustPolicyOnRole()

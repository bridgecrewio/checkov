from typing import Dict, Any, List
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_list
from checkov.common.util.oidc_utils import gh_abusable_claims, gh_repo_regex


class AzureGithubActionsOIDCTrustPolicy(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Azure GitHub Actions OIDC trust policy is configured securely"
        id = "CKV_AZURE_249"
        supported_resources = [
            "azuread_application_federated_identity_credential",
        ]
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def validate_subject_claim(self, subject: str) -> bool:
        """Validates the subject claim for security concerns"""
        if not subject:
            return False

        # If no colons - invalid format for GitHub Actions claims
        if ":" not in subject:
            return False

        claim_parts = subject.split(":")

        # Check for wildcards in critical positions
        if claim_parts[0] == "*" or claim_parts[1] == "*":
            return False

        # Check for abusable claims
        if claim_parts[0] in gh_abusable_claims:
            return False

        # Validate repo format if repo claim is used
        if claim_parts[0] == "repo":
            if not gh_repo_regex.match(claim_parts[1]):
                return False

        return True

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """Scans the configuration for Azure GitHub Actions OIDC trust policy"""
        try:
            condition = force_list(conf.get("subject", [None]))[0]
            if not condition:
                return CheckResult.FAILED

            # We should have colon delimited subject claim
            if ":" not in condition or condition == "*":
                return CheckResult.FAILED

            # At this point we know we have a colon delimited subject claim, so length should be at least 2
            split_condition = condition.split(":")

            # First check -> wildcards
            if "*" == split_condition[0] or "*" == split_condition[1]:
                return CheckResult.FAILED

            # Second check -> abusable claims
            if split_condition[0] in gh_abusable_claims:
                return CheckResult.FAILED

            # Third check -> repo format
            if split_condition[0] == "repo" and not gh_repo_regex.match(split_condition[1]):
                return CheckResult.FAILED

            return CheckResult.PASSED

        except Exception:
            return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["identity_federation/subject", "subject"]


check = AzureGithubActionsOIDCTrustPolicy()

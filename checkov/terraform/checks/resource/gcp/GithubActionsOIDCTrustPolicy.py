from typing import Dict, Any, List
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.oidc_utils import gh_abusable_claims, gh_repo_regex
import re


class GithubActionsOIDCTrustPolicy(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure GCP GitHub Actions OIDC trust policy is configured securely"
        id = "CKV_GCP_125"
        supported_resources = ["google_iam_workload_identity_pool_provider"]
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def extract_sub_claim_value(self, condition: str) -> str:
        """Extract the claim value from the condition string."""
        if not condition:
            return ""

        # Handle both single and double quotes
        claim_match = re.search(r"assertion\.sub\s*==\s*['\"]([^'\"]+)['\"]", condition)
        if claim_match:
            return claim_match.group(1)
        return ""

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """Scans the configuration for GitHub Actions OIDC trust policy"""
        try:
            # Check issuer URI
            issuer_uri = conf.get("issuer_uri", [None])[0]
            print(f"Issuer URI: {issuer_uri}")
            if not issuer_uri or issuer_uri != "https://token.actions.githubusercontent.com":
                print("Failed: Invalid issuer URI")
                return CheckResult.FAILED

            # Check attribute mapping
            attribute_mapping = conf.get("attribute_mapping")
            if not attribute_mapping or not isinstance(attribute_mapping, list) or not attribute_mapping[0]:
                return CheckResult.FAILED
            attribute_mapping = attribute_mapping[0]
            if not attribute_mapping or "google.subject" not in attribute_mapping:
                print("Failed: Missing google.subject in attribute mapping")
                return CheckResult.FAILED

            # Check attribute condition
            attribute_condition = conf.get("attribute_condition", False)[0]
            if not attribute_condition:
                return CheckResult.FAILED

            # Extract claim value
            sub_claim_value = self.extract_sub_claim_value(attribute_condition)
            if not sub_claim_value:
                print("Failed: Could not extract claim value")
                return CheckResult.FAILED

            # If no colons - it means we assert something the value without the claim name, which is invalid when using GitHub Actions OIDC
            if ":" not in sub_claim_value:
                print("Failed: Invalid claim value")
                return CheckResult.FAILED

            # Break by colons; Since we already checked for the presence of colons, we can safely assume that the claim is in the form of claim_name:claim_value
            claim_parts = sub_claim_value.split(":")
            # Check if the first claim or value are wildcards - if yes, the assertion is checking nothing
            if claim_parts[0] == "*" or claim_parts[1] == "*":
                print("Failed: Wildcard claims")
                return CheckResult.FAILED

            # Check if the first claim is an abusable claim - if yes, the whole assertion can be abused
            if claim_parts[0] in gh_abusable_claims:
                print("Failed: Abusable claim")
                return CheckResult.FAILED

            # Lastly, check for the classic "repo" claim
            if claim_parts[0] == "repo":
                # Check if the repo claim is in the form of org/repo
                if not gh_repo_regex.match(claim_parts[1]):
                    print("Failed: Invalid repo claim")
                    return CheckResult.FAILED

            return CheckResult.PASSED

        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return CheckResult.FAILED

        def get_evaluated_keys(self) -> List[str]:
            return ["attribute_condition", "attribute_mapping", "issuer_uri"]


check = GithubActionsOIDCTrustPolicy()

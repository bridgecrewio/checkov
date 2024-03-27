from typing import Dict, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

DISALLOWED_MEMBERS = {"allUsers", "allAuthenticatedUsers"}


class GoogleKMSKeyIsPublic(BaseResourceCheck):
    def __init__(self) -> None:
        """
        ensure key is not publicly available
        KMS Crypto Key policy should not set 'allUsers' or 'allAuthenticatedUsers' in the attribute 'member'/'members'
        """
        name = "Ensure KMS policy should not allow public access"
        id = "CKV_GCP_112"
        supported_resources = (
            "google_kms_crypto_key_iam_policy",
            "google_kms_crypto_key_iam_binding",
            "google_kms_crypto_key_iam_member",
        )
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        policy_data = conf.get("policy_data")
        if policy_data and isinstance(policy_data, list):
            for policy in policy_data:
                if not isinstance(policy, dict):
                    continue
                bindings = policy.get("bindings")
                if bindings and isinstance(bindings, list):
                    for binding in bindings:
                        members = binding.get("members")
                        if members and isinstance(members, list):
                            for member in members:
                                if member in DISALLOWED_MEMBERS:
                                    return CheckResult.FAILED
            return CheckResult.PASSED

        members = conf.get("members")
        if members and isinstance(members, list):
            for member in members[0]:
                if member in DISALLOWED_MEMBERS:
                    return CheckResult.FAILED
            return CheckResult.PASSED

        member = conf.get("member")
        if member and isinstance(member, list):
            if member[0] in DISALLOWED_MEMBERS:
                return CheckResult.FAILED
            return CheckResult.PASSED

        return CheckResult.UNKNOWN


check = GoogleKMSKeyIsPublic()

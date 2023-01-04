from typing import Dict, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GoogleKMSKeyIsPublic(BaseResourceCheck):
    def __init__(self) -> None:
        """
        ensure key is not publicly available
        KMS Crypto Key policy should not set 'allUsers' or 'allAuthenticatedUsers' in the attribute 'member'/'members'
        """
        name = "KMS policy should not define public access"
        id = "CKV_GCP_112"
        supported_resources = ["google_kms_crypto_key_iam_policy", "google_kms_crypto_key_iam_binding",
                               'google_kms_crypto_key_iam_member']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        fails = ["allUsers", "allAuthenticatedUsers"]
        if conf.get("policy_data") and isinstance(conf.get("policy_data"), list):
            policy_data = conf.get("policy_data")
            for policy in policy_data:
                bindings = policy.get("bindings")
                for binding in bindings:
                    if binding.get("members") and isinstance(binding.get("members"), list):
                        members = binding.get("members")
                        for member in members:
                            if member in fails:
                                return CheckResult.FAILED
            return CheckResult.PASSED
        if conf.get("members") and isinstance(conf.get("members"), list):
            members = conf.get("members")[0]
            for member in members:
                if member in fails:
                    return CheckResult.FAILED
            return CheckResult.PASSED
        if conf.get("member") and isinstance(conf.get("member"), list):
            member = conf.get("member")[0]
            if member in fails:
                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = GoogleKMSKeyIsPublic()

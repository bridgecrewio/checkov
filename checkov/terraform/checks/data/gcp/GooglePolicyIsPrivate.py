from typing import Dict, List, Any

from checkov.terraform.checks.data.base_check import BaseDataCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GooglePolicyIsPrivate(BaseDataCheck):
    def __init__(self) -> None:
        """
        ensure policy defined is not public
        policy should not set 'allUsers' or 'allAuthenticatedUsers' in the attribute 'member'/'members'
        """
        name = "Ensure IAM policy should not define public access"
        id = "CKV_GCP_113"
        supported_data = ("google_iam_policy",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_data=supported_data)

    def scan_data_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """
            validates gcp policy
        """
        fails = ["allUsers", "allAuthenticatedUsers"]
        if conf.get("binding") and isinstance(conf.get("binding"), list):
            bindings = conf.get("binding")
            for binding in bindings:
                if binding.get("members") and isinstance(binding.get("members"), list):
                    members = binding.get("members")[0]
                    for member in members:
                        if member in fails:
                            self.evaluated_keys = ["bindings/[0]/members"]
                            return CheckResult.FAILED
                    return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = GooglePolicyIsPrivate()

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from checkov.terraform.checks.resource.base_cloudsplaining_resource_iam_check import (
    BaseTerraformCloudsplainingResourceIAMCheck,
)

if TYPE_CHECKING:
    from cloudsplaining.scan.policy_document import PolicyDocument


class IAMStarResourcePolicyDocument(BaseTerraformCloudsplainingResourceIAMCheck):
    def __init__(self):
        name = 'Ensure no IAM policies documents allow "*" as a statement\'s resource for restrictable actions'
        id = "CKV_AWS_355"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> list[str] | list[dict[str, Any]]:
        return policy.all_allowed_unrestricted_actions


check = IAMStarResourcePolicyDocument()

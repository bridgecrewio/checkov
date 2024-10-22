from __future__ import annotations

from typing import Any, TYPE_CHECKING

from checkov.terraform.checks.data.base_cloudsplaining_data_iam_check import BaseTerraformCloudsplainingDataIAMCheck

if TYPE_CHECKING:
    from cloudsplaining.scan.policy_document import PolicyDocument


class ResourcePolicyDocument(BaseTerraformCloudsplainingDataIAMCheck):
    def __init__(self) -> None:
        name = 'Ensure no IAM policies documents allow "*" as a statement\'s resource for restrictable actions'
        id = "CKV_AWS_356"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> list[str] | list[dict[str, Any]]:
        return policy.all_allowed_unrestricted_actions


check = ResourcePolicyDocument()

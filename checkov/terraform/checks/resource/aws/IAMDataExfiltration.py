from __future__ import annotations

from typing import List, TYPE_CHECKING

from checkov.terraform.checks.resource.base_cloudsplaining_resource_iam_check import BaseTerraformCloudsplainingResourceIAMCheck

if TYPE_CHECKING:
    from cloudsplaining.scan.policy_document import PolicyDocument


class IAMDataExfiltration(BaseTerraformCloudsplainingResourceIAMCheck):
    def __init__(self) -> None:
        name = "Ensure IAM policies does not allow data exfiltration"
        id = "CKV_AWS_288"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> List[str]:
        return policy.allows_data_exfiltration_actions


check = IAMDataExfiltration()

from __future__ import annotations

from typing import List, TYPE_CHECKING

from checkov.terraform.checks.data.base_cloudsplaining_data_iam_check import BaseTerraformCloudsplainingDataIAMCheck

if TYPE_CHECKING:
    from cloudsplaining.scan.policy_document import PolicyDocument


class CloudSplainingDataExfiltration(BaseTerraformCloudsplainingDataIAMCheck):
    def __init__(self) -> None:
        name = "Ensure IAM policies does not allow data exfiltration"
        id = "CKV_AWS_108"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> List[str]:
        return policy.allows_data_exfiltration_actions


check = CloudSplainingDataExfiltration()

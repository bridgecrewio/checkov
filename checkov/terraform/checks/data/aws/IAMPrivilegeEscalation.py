from __future__ import annotations

from typing import List, Dict, Any, Union, TYPE_CHECKING

from checkov.terraform.checks.data.base_cloudsplaining_data_iam_check import BaseTerraformCloudsplainingDataIAMCheck

if TYPE_CHECKING:
    from cloudsplaining.scan.policy_document import PolicyDocument


class CloudSplainingPrivilegeEscalation(BaseTerraformCloudsplainingDataIAMCheck):
    def __init__(self) -> None:
        name = "Ensure IAM policies does not allow privilege escalation"
        id = "CKV_AWS_110"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> Union[List[str], List[Dict[str, Any]]]:
        return policy.allows_privilege_escalation


check = CloudSplainingPrivilegeEscalation()

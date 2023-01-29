from __future__ import annotations

from typing import Union, List, Dict, Any, TYPE_CHECKING

from checkov.terraform.checks.data.base_cloudsplaining_data_iam_check import BaseTerraformCloudsplainingDataIAMCheck

if TYPE_CHECKING:
    from cloudsplaining.scan.policy_document import PolicyDocument


class CloudSplainingWriteAccess(BaseTerraformCloudsplainingDataIAMCheck):
    def __init__(self) -> None:
        name = "Ensure IAM policies does not allow write access without constraints"
        id = "CKV_AWS_111"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> Union[List[str], List[Dict[str, Any]]]:
        return policy.write_actions_without_constraints


check = CloudSplainingWriteAccess()

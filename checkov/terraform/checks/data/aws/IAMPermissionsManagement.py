from __future__ import annotations

from typing import List, Dict, Any, Union, TYPE_CHECKING

from checkov.terraform.checks.data.base_cloudsplaining_data_iam_check import BaseTerraformCloudsplainingDataIAMCheck

if TYPE_CHECKING:
    from cloudsplaining.scan.policy_document import PolicyDocument


class CloudSplainingPermissionsManagement(BaseTerraformCloudsplainingDataIAMCheck):
    def __init__(self) -> None:
        name = "Ensure IAM policies does not allow permissions management / resource exposure without constraints"
        id = "CKV_AWS_109"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> Union[List[str], List[Dict[str, Any]]]:
        return policy.permissions_management_without_constraints


check = CloudSplainingPermissionsManagement()

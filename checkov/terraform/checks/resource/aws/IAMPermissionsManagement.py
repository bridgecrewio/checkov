from __future__ import annotations

from typing import List, Dict, Any, Union, TYPE_CHECKING

from checkov.terraform.checks.resource.base_cloudsplaining_resource_iam_check import BaseTerraformCloudsplainingResourceIAMCheck

if TYPE_CHECKING:
    from cloudsplaining.scan.policy_document import PolicyDocument


class IAMPermissionsManagement(BaseTerraformCloudsplainingResourceIAMCheck):
    def __init__(self) -> None:
        name = "Ensure IAM policies does not allow permissions management / resource exposure without constraints"
        id = "CKV_AWS_289"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> Union[List[str], List[Dict[str, Any]]]:
        return policy.permissions_management_without_constraints


check = IAMPermissionsManagement()

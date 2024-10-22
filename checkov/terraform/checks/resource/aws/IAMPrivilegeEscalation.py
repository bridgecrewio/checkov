from __future__ import annotations

from typing import List, Dict, Any, Union, TYPE_CHECKING

from checkov.terraform.checks.resource.base_cloudsplaining_resource_iam_check import \
    BaseTerraformCloudsplainingResourceIAMCheck

if TYPE_CHECKING:
    from cloudsplaining.scan.policy_document import PolicyDocument


class ResourceCloudSplainingPrivilegeEscalation(BaseTerraformCloudsplainingResourceIAMCheck):
    def __init__(self) -> None:
        name = "Ensure IAM policies does not allow privilege escalation"
        id = "CKV_AWS_286"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> Union[List[str], List[Dict[str, Any]]]:
        escalations = policy.allows_privilege_escalation
        flattened_escalations: list[str] = []
        if escalations:
            for escalation in escalations:
                if isinstance(escalation, dict):
                    flattened_escalations.extend(escalation.get('actions'))
                else:
                    flattened_escalations.append(escalation)
        return flattened_escalations


check = ResourceCloudSplainingPrivilegeEscalation()

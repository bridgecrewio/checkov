from typing import List, Dict, Any, Union

from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.terraform.checks.data.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck


class CloudSplainingPrivilegeEscalation(BaseCloudsplainingIAMCheck):
    def __init__(self) -> None:
        name = "Ensure IAM policies does not allow privilege escalation"
        id = "CKV_AWS_110"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> Union[List[str], List[Dict[str, Any]]]:
        return policy.allows_privilege_escalation


check = CloudSplainingPrivilegeEscalation()

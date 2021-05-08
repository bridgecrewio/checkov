from typing import Union, List, Dict, Any

from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.terraform.checks.data.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck


class CloudSplainingWriteAccess(BaseCloudsplainingIAMCheck):
    def __init__(self) -> None:
        name = "Ensure IAM policies does not allow write access without constraints"
        id = "CKV_AWS_111"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> Union[List[str], List[Dict[str, Any]]]:
        return policy.write_actions_without_constraints


check = CloudSplainingWriteAccess()

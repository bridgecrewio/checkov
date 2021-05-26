from typing import List

from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.terraform.checks.data.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck


class CloudSplainingDataExfiltration(BaseCloudsplainingIAMCheck):
    def __init__(self) -> None:
        name = "Ensure IAM policies does not allow data exfiltration"
        id = "CKV_AWS_108"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> List[str]:
        return policy.allows_data_exfiltration_actions


check = CloudSplainingDataExfiltration()

from typing import List, Union, Dict, Any

from cloudsplaining.scan.policy_document import PolicyDocument

from checkov.terraform.checks.data.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck


class CloudSplainingCredentialsExposure(BaseCloudsplainingIAMCheck):
    excluded_actions = {"ecr:GetAuthorizationToken"}

    def __init__(self) -> None:
        name = "Ensure IAM policies does not allow credentials exposure"
        id = "CKV_AWS_107"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> Union[List[str], List[Dict[str, Any]]]:
        return [x for x in policy.credentials_exposure if x not in CloudSplainingCredentialsExposure.excluded_actions]


check = CloudSplainingCredentialsExposure()

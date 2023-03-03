from __future__ import annotations

from typing import List, Union, Dict, Any, TYPE_CHECKING

from checkov.terraform.checks.data.base_cloudsplaining_data_iam_check import BaseTerraformCloudsplainingDataIAMCheck

if TYPE_CHECKING:
    from cloudsplaining.scan.policy_document import PolicyDocument


class CloudSplainingCredentialsExposure(BaseTerraformCloudsplainingDataIAMCheck):
    excluded_actions = {"ecr:GetAuthorizationToken"}  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        name = "Ensure IAM policies does not allow credentials exposure"
        id = "CKV_AWS_107"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> Union[List[str], List[Dict[str, Any]]]:
        return [x for x in policy.credentials_exposure if x not in CloudSplainingCredentialsExposure.excluded_actions]


check = CloudSplainingCredentialsExposure()

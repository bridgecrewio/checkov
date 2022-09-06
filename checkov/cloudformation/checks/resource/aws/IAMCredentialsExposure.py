from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.cloudformation.checks.resource.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck

if TYPE_CHECKING:
    from cloudsplaining.scan.policy_document import PolicyDocument


class cloudsplainingCredentialsExposure(BaseCloudsplainingIAMCheck):
    excluded_actions = {  # noqa: CCE003  # a static attribute
        "ecr:GetAuthorizationToken"
    }

    def __init__(self) -> None:
        name = "Ensure IAM policies does not allow credentials exposure"
        id = "CKV_AWS_107"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy: PolicyDocument) -> list[str]:
        credentials_exposure_actions = policy.credentials_exposure
        return [
            x for x in credentials_exposure_actions
            if x not in cloudsplainingCredentialsExposure.excluded_actions
        ]


check = cloudsplainingCredentialsExposure()

from checkov.cloudformation.checks.resource.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck


class cloudsplainingCredentialsExposure(BaseCloudsplainingIAMCheck):
    excluded_actions = {
        "ecr:GetAuthorizationToken"
    }

    def __init__(self):
        name = "Ensure IAM policies does not allow credentials exposure"
        id = "CKV_AWS_107"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy):
        credentials_exposure_actions = policy.credentials_exposure
        return [
            x for x in credentials_exposure_actions
            if x not in cloudsplainingCredentialsExposure.excluded_actions
        ]


check = cloudsplainingCredentialsExposure()

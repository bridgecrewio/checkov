from checkov.terraform.checks.data.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck


class CloudSplainingCredentialsExposure(BaseCloudsplainingIAMCheck):
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
            if x not in CloudSplainingCredentialsExposure.excluded_actions
        ]


check = CloudSplainingCredentialsExposure()

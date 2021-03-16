from checkov.cloudformation.checks.resource.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck


class cloudsplainingCredentialsExposure(BaseCloudsplainingIAMCheck):

    def __init__(self):
        name = "Ensure IAM policies does not allow credentials exposure"
        id = "CKV_AWS_107"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy):
        return policy.credentials_exposure


check = cloudsplainingCredentialsExposure()

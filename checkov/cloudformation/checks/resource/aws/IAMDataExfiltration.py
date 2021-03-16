from checkov.cloudformation.checks.resource.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck


class cloudsplainingDataExfiltration(BaseCloudsplainingIAMCheck):

    def __init__(self):
        name = "Ensure IAM policies does not allow data exfiltration"
        id = "CKV_AWS_108"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy):
        return policy.allows_data_exfiltration_actions


check = cloudsplainingDataExfiltration()

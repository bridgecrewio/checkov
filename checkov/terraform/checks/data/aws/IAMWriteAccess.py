from checkov.terraform.checks.data.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck


class CloudSplainingWriteAccess(BaseCloudsplainingIAMCheck):

    def __init__(self):
        name = "Ensure IAM policies does not allow write access without constraints"
        id = "CKV_AWS_111"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy):
        return policy.write_actions_without_constraints


check = CloudSplainingWriteAccess()

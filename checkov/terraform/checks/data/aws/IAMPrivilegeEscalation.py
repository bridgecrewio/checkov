from checkov.terraform.checks.data.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck


class CloudSplainningPrivilegeEscalation(BaseCloudsplainingIAMCheck):

    def __init__(self):
        name = "Ensure IAM policies does not allow privilege escalation"
        id = "CKV_AWS_105"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy):
        escalation = policy.allows_privilege_escalation
        return escalation


check = CloudSplainningPrivilegeEscalation()

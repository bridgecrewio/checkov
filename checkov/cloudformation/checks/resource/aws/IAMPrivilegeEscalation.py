from checkov.cloudformation.checks.resource.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck


class cloudsplainingPrivilegeEscalation(BaseCloudsplainingIAMCheck):

    def __init__(self):
        name = "Ensure IAM policies does not allow privilege escalation"
        id = "CKV_AWS_110"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy):
        escalation = policy.allows_privilege_escalation
        return escalation


check = cloudsplainingPrivilegeEscalation()

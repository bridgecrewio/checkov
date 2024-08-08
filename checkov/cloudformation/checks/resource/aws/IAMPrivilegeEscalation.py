from checkov.cloudformation.checks.resource.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck


class cloudsplainingPrivilegeEscalation(BaseCloudsplainingIAMCheck):

    def __init__(self):
        name = "Ensure IAM policies does not allow privilege escalation"
        id = "CKV_AWS_110"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy):
        escalations = policy.allows_privilege_escalation
        flattened_escalations: list[str] = []
        if escalations:
            for escalation in escalations:
                if isinstance(escalation, dict):
                    flattened_escalations.extend(escalation.get('actions'))
                else:
                    flattened_escalations.append(escalation)
        return flattened_escalations


check = cloudsplainingPrivilegeEscalation()

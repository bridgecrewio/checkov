from checkov.cloudformation.checks.resource.BaseCloudsplainingIAMCheck import BaseCloudsplainingIAMCheck


class cloudsplainingPermissionsManagement(BaseCloudsplainingIAMCheck):

    def __init__(self):
        name = "Ensure IAM policies does not allow permissions management without constraints"
        id = "CKV_AWS_109"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy):
        return policy.permissions_management_without_constraints


check = cloudsplainingPermissionsManagement()

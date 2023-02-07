from checkov.terraform.checks.resource.base_cloudsplaining_resource_iam_check import BaseTerraformCloudsplainingResourceIAMCheck


class cloudsplainingWriteAccess(BaseTerraformCloudsplainingResourceIAMCheck):

    def __init__(self):
        name = "Ensure IAM policies does not allow write access without constraints"
        id = "CKV_AWS_290"
        super().__init__(name=name, id=id)

    def cloudsplaining_analysis(self, policy):
        return policy.write_actions_without_constraints


check = cloudsplainingWriteAccess()

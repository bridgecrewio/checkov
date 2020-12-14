from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.gcp.AbsGoogleImpersonationRoles import AbsGoogleImpersonationRoles

class GoogleProjectImpersonationRoles(AbsGoogleImpersonationRoles):
    def __init__(self):
        name = "Ensure no roles that enable to impersonate and manage all service accounts are used at a project level"
        id = "CKV_GCP_49"
        supported_resources = ['google_project_iam_member', 'google_project_iam_binding']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)


check = GoogleProjectImpersonationRoles()

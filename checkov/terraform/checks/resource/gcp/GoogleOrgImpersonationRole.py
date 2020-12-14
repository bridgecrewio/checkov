from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.gcp.AbsGoogleImpersonationRoles import AbsGoogleImpersonationRoles

class GoogleOrgImpersonationRoles(AbsGoogleImpersonationRoles):
    def __init__(self):
        name = "Ensure no roles that enable to impersonate and manage all service accounts are used at an organization level"
        id = "CKV_GCP_45"
        supported_resources = ['google_organization_iam_member', 'google_organization_iam_binding']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)


check = GoogleOrgImpersonationRoles()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.gcp.AbsGoogleBasicRoles import AbsGoogleBasicRoles


class GoogleOrgBasicRoles(AbsGoogleBasicRoles):
    def __init__(self) -> None:
        name = "Ensure basic roles are not used at organization level."
        id = "CKV_GCP_115"
        supported_resources = ('google_organization_iam_member', 'google_organization_iam_binding')
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)


check = GoogleOrgBasicRoles()

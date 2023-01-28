from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.gcp.AbsGoogleBasicRoles import AbsGoogleBasicRoles


class GoogleOrgBasicRoles(AbsGoogleBasicRoles):
    def __init__(self) -> None:
        name = "Usage of basic roles at organization level should be avoided."
        id = "CKV_GCP_113"
        supported_resources = ('google_organization_iam_member', 'google_organization_iam_binding')
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)


check = GoogleOrgBasicRoles()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.gcp.AbsGoogleBasicRoles import AbsGoogleBasicRoles


class GoogleProjectBasicRoles(AbsGoogleBasicRoles):
    def __init__(self) -> None:
        name = "Usage of basic roles at project level should be avoided."
        id = "CKV_GCP_117"
        supported_resources = ('google_project_iam_member', 'google_project_iam_binding')
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)


check = GoogleProjectBasicRoles()

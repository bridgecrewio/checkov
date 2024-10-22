from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.gcp.AbsGoogleImpersonationRoles import AbsGoogleImpersonationRoles


class GoogleFolderImpersonationRoles(AbsGoogleImpersonationRoles):
    def __init__(self) -> None:
        name = "Ensure no roles that enable to impersonate and manage all service accounts are used at a folder level"
        id = "CKV_GCP_44"
        supported_resources = ('google_folder_iam_member', 'google_folder_iam_binding')
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)


check = GoogleFolderImpersonationRoles()

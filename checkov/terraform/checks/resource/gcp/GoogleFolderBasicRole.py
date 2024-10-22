from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.gcp.AbsGoogleBasicRoles import AbsGoogleBasicRoles


class GoogleFolderBasicRoles(AbsGoogleBasicRoles):
    def __init__(self) -> None:
        name = "Ensure basic roles are not used at folder level."
        id = "CKV_GCP_116"
        supported_resources = ('google_folder_iam_member', 'google_folder_iam_binding')
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)


check = GoogleFolderBasicRoles()

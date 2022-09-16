from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.gcp.AbsGoogleIAMMemberDefaultServiceAccount import AbsGoogleIAMMemberDefaultServiceAccount


class GoogleFolderMemberDefaultServiceAccount(AbsGoogleIAMMemberDefaultServiceAccount):
    def __init__(self) -> None:
        name = "Ensure Default Service account is not used at a folder level"
        id = "CKV_GCP_48"
        supported_resources = ('google_folder_iam_member', 'google_folder_iam_binding')
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)


check = GoogleFolderMemberDefaultServiceAccount()

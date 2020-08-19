from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.gcp.AbsGoogleDefaultSAImpersonationRole import AbsGoogleDefaultSAImpersonationRole

class GoogleProjectDefaultSAImpersonationRole(AbsGoogleDefaultSAImpersonationRole):
    def __init__(self):
        name = "Ensure that Service Account has no Admin privileges"
        id = "CKV_GCP_46"
        supported_resources = ['google_project_iam_member', 'google_project_iam_binding']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)


check = GoogleProjectDefaultSAImpersonationRole()

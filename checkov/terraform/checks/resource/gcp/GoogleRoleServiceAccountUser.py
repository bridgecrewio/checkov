from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GoogleRoleServiceAccountUser(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that IAM users are not assigned the Service Account User or Service Account Token Creator roles \
         at project level"
        id = "CKV_GCP_41"
        supported_resources = ['google_project_iam_binding', 'google_project_iam_member']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'role' in conf.keys():
            if conf['role'][0] not in ['roles/iam.serviceAccountUser', 'roles/iam.serviceAccountTokenCreator']:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleRoleServiceAccountUser()

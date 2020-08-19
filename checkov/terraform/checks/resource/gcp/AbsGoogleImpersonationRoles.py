from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

IMPERSONATION_ROLES = [
    "roles/owner",
    "roles/editor",
    "roles/iam.securityAdmin",
    "roles/iam.serviceAccountAdmin",
    "roles/iam.serviceAccountKeyAdmin",
    "roles/iam.serviceAccountUser",
    "roles/iam.serviceAccountTokenCreator",
    "roles/iam.workloadIdentityUser",
    "roles/dataproc.editor",
    "roles/dataproc.admin",
    "roles/dataflow.developer",
    "roles/resourcemanager.folderAdmin",
    "roles/resourcemanager.folderIamAdmin",
    "roles/resourcemanager.projectIamAdmin",
    "roles/resourcemanager.organizationAdmin",
    "roles/serverless.serviceAgent",
    "roles/dataproc.serviceAgent",
]


class AbsGoogleImpersonationRoles(BaseResourceCheck):
    def __init__(self, name, id, categories, supported_resources):
        super().__init__(name, id, categories, supported_resources)

    def scan_resource_conf(self, conf):
        if 'role' in conf and conf['role'][0] in IMPERSONATION_ROLES:
            return CheckResult.FAILED
        return CheckResult.PASSED

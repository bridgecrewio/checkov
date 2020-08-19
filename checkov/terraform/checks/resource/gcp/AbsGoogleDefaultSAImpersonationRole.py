import re

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

DENIED_ROLES = [
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

# Default Compute -compute@developer.gserviceaccount.com
# Default App Spot @appspot.gserviceaccount.com
DEFAULT_SA = re.compile(".*-compute@developer\.gserviceaccount\.com|.*@appspot\.gserviceaccount\.com")


class AbsGoogleDefaultSAImpersonationRole(BaseResourceCheck):
    def __init__(self, name, id, categories, supported_resources):
        super().__init__(name, id, categories, supported_resources)

    def scan_resource_conf(self, conf):
        members_conf = []
        if 'members' in conf:
            members_conf = conf['members'][0]
        elif 'member' in conf:
            members_conf = conf['member']
        if 'role' in conf and conf['role'][0] in DENIED_ROLES and \
                any(re.match(DEFAULT_SA, member) for member in members_conf):
            return CheckResult.FAILED
        return CheckResult.PASSED

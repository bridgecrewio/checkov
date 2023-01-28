from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

BASIC_ROLES = [
    "roles/owner",
    "roles/editor",
    "roles/viewer",
]

class AbsGoogleBasicRoles(BaseResourceCheck):
    def scan_resource_conf(self, conf):
        self.evaluated_keys = ['role']
        if 'role' in conf and conf['role'][0] in BASIC_ROLES:
            return CheckResult.FAILED
        return CheckResult.PASSED

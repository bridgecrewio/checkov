from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
import re

USER_MANAGED_SERVICE_ACCOUNT = re.compile ('.*@.*\.iam\.gserviceaccount\.com$')
ADMIN_ROLE = re.compile ('.*(.*Admin|.*admin|editor|owner)')


class GoogleProjectAdminServiceAccount(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Service Account has no Admin privileges"
        id = "CKV_GCP_42"
        supported_resources = ['google_project_iam_member']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'member' in conf.keys():
            if re.match(USER_MANAGED_SERVICE_ACCOUNT, str(conf['member'][0])):
                if re.match(ADMIN_ROLE, str(conf['role'][0])):
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = GoogleProjectAdminServiceAccount()

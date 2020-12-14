from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck

class PrivateRepo(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Repository is Private"
        id = "CKV_GIT_1"
        supported_resources = ['github_repository']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'private' in conf:
            if conf['private'] == [True]:
                return CheckResult.PASSED
        elif 'visibility' in conf:
            if conf['visibility'] == ['private'] or conf['visibility'] == ['internal']:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = PrivateRepo()

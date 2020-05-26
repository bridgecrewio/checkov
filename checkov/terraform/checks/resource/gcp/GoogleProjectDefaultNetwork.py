from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GoogleProjectDefaultNetwork(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that the default network does not exist in a project"
        id = "CKV_GCP_27"
        supported_resources = ['google_project']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        https://www.terraform.io/docs/providers/google/r/google_project.html
        :param conf: google_project configuration
        :return: <CheckResult>
        """
        if 'auto_create_network' in conf.keys():
            if not conf['auto_create_network'][0]:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleProjectDefaultNetwork()

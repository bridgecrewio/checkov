from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class ArbitraryCommandWithNullResource(BaseResourceCheck):

    def __init__(self):
        """
        Using the null resource and local-exec can be used to execute arbitrary code
        """
        name = "Ensure Create before destroy for API Gateway"
        id = "CKV_TF_3"
        supported_resources = ['null_resource']
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'provisioner' in conf:
            for provisioner in conf['provisioner']:
                if isinstance(provisioner, dict) and 'local-exec' in provisioner:
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = ArbitraryCommandWithNullResource()

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.module.base_module_check import BaseModuleCheck


class ModuleCheck(BaseModuleCheck):
    def __init__(self):
        name = "Some test for module calls"
        id = "CKV_M_999"
        supported_resources = ['module']
        categories = []
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_module_conf(self, conf):
        """
        Some test for module source
        :param conf: module call
        :return: <CheckResult>
        """
        return CheckResult.PASSED if 'source' in conf.keys() else CheckResult.FAILED


scanner = ModuleCheck()

from packaging import version as v

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.module.base_module_check import BaseModuleCheck


class S3ModuleVersionCheck(BaseModuleCheck):
    def __init__(self):
        name = "Ensure S3 module is from version 0.47.0"
        id = "CKV_TF_MODULE_1"
        supported_resources = ['module']
        categories = []
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_module_conf(self, conf):
        """
        Some test for module source
        :param conf: module call
        :return: <CheckResult>
        """

        version = conf.get('version', [])
        if not version:
            # latest version is used
            return CheckResult.PASSED
        else:
            if v.parse(version[0]) <= v.parse("0.3.4"):
                # misconfigured version is used
                return CheckResult.FAILED
            # good version is used
            return CheckResult.PASSED


scanner = S3ModuleVersionCheck()

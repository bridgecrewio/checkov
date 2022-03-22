import re

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.module.base_module_check import BaseModuleCheck

MODULE_GIT_VERSION_PATTERN = re.compile(r"git::https?:\/\/[^\/]+\/.+.git\?ref=(\b[0-9a-f]{5,40}\b)")


class ModuleSourceHashCheck(BaseModuleCheck):
    def __init__(self):
        name = "Ensure module is immutable using commit hash"
        id = "CKV_TF_MODULE_2"
        supported_resources = ['module']
        categories = []
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_module_conf(self, conf):
        """
        Some test for module source
        :param conf: module call
        :return: <CheckResult>
        """

        source = conf.get('source', [])
        if not source:
            # source is using latest or tagged version
            return CheckResult.FAILED
        else:
            if MODULE_GIT_VERSION_PATTERN.match(source[0]):
                # immutable source is being used
                return CheckResult.PASSED
            # non immutable source is used
            return CheckResult.FAILED


scanner = ModuleSourceHashCheck()

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check

class ApiServerAdmissionControlEventRateLimit(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_78"
        name = "Ensure that the admission control plugin EventRateLimit is set"
        categories = [CheckCategories.KUBERNETES]
        supported_kind = ['AdmissionConfiguration']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf):
        if "plugins" not in conf:
            return CheckResult.FAILED
        plugins = conf["plugins"]
        for plugin in plugins:
            if plugin["name"] == "EventRateLimit":
                return CheckResult.PASSED

        return CheckResult.FAILED

check = ApiServerAdmissionControlEventRateLimit()

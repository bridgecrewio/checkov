from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class ReadinessProbe(BaseK8Check):

    def __init__(self):
        name = "Readiness Probe Should be Configured"
        id = "CKV_K8S_9"
        # initContainers do not need Readiness Probes...
        # Location: container .readinessProbe
        supported_kind = ['containers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return conf['parent']

    def scan_spec_conf(self, conf):
        # Don't check Job/CronJob
        if "parent" in conf:
            if "Job" in conf["parent"]:
                return CheckResult.PASSED
        if "readinessProbe" not in conf:
            return CheckResult.FAILED
        return CheckResult.PASSED

check = ReadinessProbe()
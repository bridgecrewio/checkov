from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class LivenessProbe(BaseK8Check):

    def __init__(self):
        name = "Liveness Probe Should be Configured"
        id = "CKV_K8S_8"
        # initContainers do not need Liveness Probes...
        # Location: container .livenessProbe
        supported_kind = ['containers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        # Don't check Job/CronJob
        if "parent" in conf:
            if "Job" in conf["parent"]:
                return CheckResult.PASSED
        if "livenessProbe" not in conf:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = LivenessProbe()

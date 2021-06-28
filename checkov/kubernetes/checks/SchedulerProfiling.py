from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class SchedulerProfiling(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_114"
        name = "Ensure that the --profiling argument is set to false"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories,
                         supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if "command" in conf:
            if "kube-scheduler" in conf["command"]:
                if "--profiling=false" not in conf["command"]:
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = SchedulerProfiling()

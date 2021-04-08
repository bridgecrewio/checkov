from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class KubeControllerManagerTerminatedPods(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_106"
        name = "Ensure that the --terminated-pod-gc-threshold argument is set as appropriate"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if conf.get("command") is not None:
            if "kube-controller-manager" in conf["command"]:
                for command in conf["command"]:
                    if command.startswith('--terminated-pod-gc-threshold'):
                        threshold = command.split("=")[1]
                        if int(threshold) > 0:
                            return CheckResult.PASSED
                        else:
                            return CheckResult.FAILED
            return CheckResult.FAILED
        return CheckResult.PASSED


check = KubeControllerManagerTerminatedPods()

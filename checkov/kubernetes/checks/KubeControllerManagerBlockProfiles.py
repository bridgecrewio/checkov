from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class KubeControllerManagerBlockProfiles(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_107"
        name = "Ensure that the --profiling argument is set to false"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if conf.get("command") is not None:
            if "kube-controller-manager" in conf["command"]:
                for command in conf["command"]:
                    if command.startswith('--profiling'):
                        value = command.split("=")[1]
                        if value == 'false':
                            return CheckResult.PASSED
                return CheckResult.FAILED
        return CheckResult.PASSED


check = KubeControllerManagerBlockProfiles()

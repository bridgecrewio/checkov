from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check

class KubeletAuthorizationModeNotAlwaysAllow(BaseK8Check):
    def __init__(self):
        # CIS-1.6 4.2.
        id = "CKV_K8S_139"
        name = "Ensure that the --authorization-mode argument is not set to AlwaysAllow"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if conf.get("command") is not None:
            if "kubelet" in conf["command"]:
                for command in conf["command"]:
                    if command.startswith("--authorization-mode"):
                        modes = command.split("=")[1]
                        if "AlwaysAllow" in modes.split(","):
                            return CheckResult.FAILED
                        break
           
        return CheckResult.PASSED

check = KubeletAuthorizationModeNotAlwaysAllow()
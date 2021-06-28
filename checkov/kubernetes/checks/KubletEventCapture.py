
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class KubletEventCapture(BaseK8Check):
    def __init__(self):
        # CIS-1.6 4.2.9
        id = "CKV_K8S_147"
        name = "Ensure that the --event-qps argument is set to 0 or a level which ensures appropriate event capture"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories,
                         supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if "command" in conf:
            if "kubelet" in conf["command"]:
                for cmd in conf["command"]:
                    if "=" in cmd:
                        [key, value, *_] = cmd.split("=")
                        if key == "--event-qps":
                            if int(value) > 5:
                                return CheckResult.FAILED

        return CheckResult.PASSED


check = KubletEventCapture()

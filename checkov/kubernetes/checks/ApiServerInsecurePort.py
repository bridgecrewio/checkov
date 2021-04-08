from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check

class ApiServerInsecurePort(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_88"
        name = "Ensure that the --insecure-port argument is set to 0"
        categories = [CheckCategories.KUBERNETES]
        supported_kind = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if "command" in conf:
            if "kube-apiserver" in conf["command"]:
                if "--insecure-port=0" not in conf["command"]:
                    return CheckResult.FAILED

        return CheckResult.PASSED

check = ApiServerInsecurePort()

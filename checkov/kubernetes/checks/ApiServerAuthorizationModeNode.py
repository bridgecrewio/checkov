from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check

class ApiServerAuthorizationModeNode(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_75"
        name = "Ensure that the --authorization-mode argument includes Node"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                hasNodeAuthorizationMode = False
                for command in conf["command"]:
                    if command.startswith("--authorization-mode"):
                        modes = command.split("=")[1]
                        if "Node" in modes.split(","):
                            hasNodeAuthorizationMode = True
                return CheckResult.PASSED if hasNodeAuthorizationMode else CheckResult.FAILED
           
        return CheckResult.PASSED

check = ApiServerAuthorizationModeNode()

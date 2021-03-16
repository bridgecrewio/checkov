from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class KubletRotateKubeletServerCertificate(BaseK8Check):
    def __init__(self):
        # CIS-1.6 4.2.12
        id = "CKV_K8S_150"
        name = "Ensure that the RotateKubeletServerCertificate argument is set to true"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories,
                         supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if "command" in conf:
            if "kubelet" in conf["command"]:
                for cmd in conf["command"]:
                    if cmd.startswith("--feature-gates"):
                        value = cmd[cmd.index("=")+1:]
                        if 'RotateKubeletServerCertificate=false' in value:
                            return CheckResult.FAILED

        return CheckResult.PASSED


check = KubletRotateKubeletServerCertificate()
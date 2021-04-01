from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class KubeControllerManagerRootCAFile(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_111"
        name = "Ensure that the --root-ca-file argument is set as appropriate"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if conf.get("command") is not None:
            if "kube-controller-manager" in conf["command"]:
                for command in conf["command"]:
                    if command.startswith('--root-ca-file'):
                        file_name = command.split("=")[1]
                        extension = file_name.split(".")[1]
                        if extension == 'pem':
                            return CheckResult.PASSED
                        else:
                            return CheckResult.FAILED
        return CheckResult.PASSED


check = KubeControllerManagerRootCAFile()

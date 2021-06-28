
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class KubeletClientCa(BaseK8Check):
    def __init__(self):
        # CIS-1.6 4.2.3
        id = "CKV_K8S_140"
        name = "Ensure that the --client-ca-file argument is set as appropriate"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if "command" in conf:
            if "kubelet" in conf["command"]:            
                for command in conf["command"]:
                    if command.startswith('--root-ca-file'):
                        file_name = command.split("=")[1]
                        extension = file_name.split(".")[1]
                        if extension == 'pem':
                            return CheckResult.PASSED
                        else:
                            return CheckResult.FAILED

        return CheckResult.PASSED


check =  KubeletClientCa()

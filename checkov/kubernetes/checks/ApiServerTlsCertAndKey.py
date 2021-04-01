from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class ApiServerTlsCertAndKey(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_100"
        name = "Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if "command" in conf and conf["command"] is not None:
            if "kube-apiserver" in conf["command"]:
                hasCertCommand = False
                hasKeyCommand = False
                for command in conf["command"]:
                    if command.startswith("--tls-cert-file"):
                        hasCertCommand = True
                    elif command.startswith("--tls-private-key-file"):
                        hasKeyCommand = True
                return CheckResult.PASSED if hasCertCommand and hasKeyCommand else CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerTlsCertAndKey()

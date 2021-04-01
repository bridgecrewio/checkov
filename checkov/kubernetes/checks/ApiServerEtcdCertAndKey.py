from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class ApiServerEtcdCertAndKey(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_99"
        name = "Ensure that the --etcd-certfile and --etcd-keyfile arguments are set as appropriate"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                hasCertCommand = False
                hasKeyCommand = False
                for command in conf["command"]:
                    if command.startswith("--etcd-certfile"):
                        hasCertCommand = True
                    elif command.startswith("--etcd-keyfile"):
                        hasKeyCommand = True
                return CheckResult.PASSED if hasCertCommand and hasKeyCommand else CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerEtcdCertAndKey()

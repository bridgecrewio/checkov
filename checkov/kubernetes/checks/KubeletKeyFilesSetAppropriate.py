
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class KubeletKeyFilesSetAppropriate(BaseK8Check):
    def __init__(self):
        # CIS-1.6 4.2.10
        id = "CKV_K8S_148"
        name = "Ensure that the --tls-cert-file and --tls-private-key-file arguments are set as appropriate"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if conf.get("command") is not None:
            if "kubelet" in conf["command"]:
                hasTLSCert = False
                hasTLSKey = False
                for command in conf["command"]:
                    if command.startswith("--tls-cert-file"):
                        hasTLSCert = True
                    elif command.startswith("--tls-private-key-file"):
                        hasTLSKey = True
                return CheckResult.PASSED if hasTLSCert and hasTLSKey else CheckResult.FAILED
           
        return CheckResult.PASSED


check =  KubeletKeyFilesSetAppropriate()

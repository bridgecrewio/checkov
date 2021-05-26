from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check
import re


class ApiServerServiceAccountKeyFile(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_97"
        name = "Ensure that the --service-account-key-file argument is set as appropriate"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if "command" in conf:
            if "kube-apiserver" in conf["command"]:
                for cmd in conf["command"]:
                    if cmd == "--service-account-key-file":
                        return CheckResult.FAILED
                    if "=" in cmd:
                        [field,value,*_] = cmd.split("=")
                        if field == "--service-account-key-file":
                            # should be a valid path and to end with .pem
                            regex = r"^([\/|\.\/]?[a-z_\-\s0-9\.]+)+\.(pem)$"
                            matches = re.match(regex, value)
                            if not matches:
                                return CheckResult.FAILED                            
        return CheckResult.PASSED

check = ApiServerServiceAccountKeyFile()

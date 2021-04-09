from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check
import re


class ApiServerRequestTimeout(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_95"
        name = "Ensure that the --request-timeout argument is set as appropriate"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if "command" in conf:
            if "kube-apiserver" in conf["command"]:
                for cmd in conf["command"]:
                    if cmd == "--request-timeout":
                        return CheckResult.FAILED  
                    if "=" in cmd:
                        [field,value] = cmd.split("=")
                        if field == "--request-timeout":
                            regex = r"^(\d{1,2}[h])(\d{1,2}[m])?(\d{1,2}[s])?$|^(\d{1,2}[m])?(\d{1,2}[s])?$|^(\d{1,2}[s])$"
                            matches = re.match(regex, value)
                            if not matches:
                                return CheckResult.FAILED                            
        return CheckResult.PASSED

check = ApiServerRequestTimeout()

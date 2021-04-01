from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check

class ApiServerAuditLogMaxAge(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_92"
        name = "Ensure that the --audit-log-maxage argument is set to 30 or as appropriate"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                hasAuditLogMaxAge = False
                for command in conf["command"]:
                    if command.startswith("--audit-log-maxage"):
                        value = command.split("=")[1]
                        hasAuditLogMaxAge = int(value) >= 30
                        break
                return CheckResult.PASSED if hasAuditLogMaxAge else CheckResult.FAILED
           
        return CheckResult.PASSED

check = ApiServerAuditLogMaxAge()
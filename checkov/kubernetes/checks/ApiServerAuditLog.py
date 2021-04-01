from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check

class ApiServerAuditLog(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_91"
        name = "Ensure that the --audit-log-path argument is set"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                hasAuditLog = False
                for command in conf["command"]:
                    if command.startswith("--audit-log-path"):
                        hasAuditLog = True
                return CheckResult.PASSED if hasAuditLog else CheckResult.FAILED
           
        return CheckResult.PASSED

check = ApiServerAuditLog()
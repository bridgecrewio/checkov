from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check

class ApiServerAuditLogMaxBackup(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_93"
        name = "Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                hasAuditLogMaxBackup = False
                for command in conf["command"]:
                    if command.startswith("--audit-log-maxbackup"):
                        value = command.split("=")[1]
                        hasAuditLogMaxBackup = int(value) >= 10
                        break
                return CheckResult.PASSED if hasAuditLogMaxBackup else CheckResult.FAILED
           
        return CheckResult.PASSED

check = ApiServerAuditLogMaxBackup()
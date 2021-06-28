from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check

class ApiServerAuditLogMaxSize(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_94"
        name = "Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                hasAuditLogMaxSize = False
                for command in conf["command"]:
                    if command.startswith("--audit-log-maxsize"):
                        value = command.split("=")[1]
                        hasAuditLogMaxSize = int(value) >= 100
                        break
                return CheckResult.PASSED if hasAuditLogMaxSize else CheckResult.FAILED
           
        return CheckResult.PASSED

check = ApiServerAuditLogMaxSize()
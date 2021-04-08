from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check

class ApiServerServiceAccountLookup(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_96"
        name = "Ensure that the --service-account-lookup argument is set to true"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                if "--service-account-lookup=false" in conf["command"] or "--service-account-lookup=true" not in conf["command"]:
                    return CheckResult.FAILED

           
        return CheckResult.PASSED

check = ApiServerServiceAccountLookup()
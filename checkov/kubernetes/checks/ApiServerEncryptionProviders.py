
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check
from checkov.kubernetes.checks.k8s_check_utils import extract_commands


class ApiServerEncryptionProviders(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_104"
        name = "Ensure that encryption providers are appropriately configured"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        keys, values = extract_commands(conf)

        if "kube-apiserver" in keys:
            if "--encryption-provider-config" not in keys:
                        return CheckResult.FAILED
        

        return CheckResult.PASSED


check =  ApiServerEncryptionProviders()

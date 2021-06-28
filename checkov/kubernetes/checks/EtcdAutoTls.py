from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class EtcdAutoTls(BaseK8Check):
    def __init__(self):
        # CIS-1.6 2.3
        id = "CKV_K8S_118"
        name = "Ensure that the --auto-tls argument is not set to true"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories,
                         supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if "etcd" in conf.get("command", []) and "--auto-tls=true" in conf.get("command", []):
            return CheckResult.FAILED

        return CheckResult.PASSED


check = EtcdAutoTls()

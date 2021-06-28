
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check
from checkov.kubernetes.checks.k8s_check_utils import extract_commands


class KubeletReadOnlyPort(BaseK8Check):
    def __init__(self):
        # CIS-1.6 4.2.4
        id = "CKV_K8S_141"
        name = "Ensure that the --read-only-port argument is set to 0"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories,
                         supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        keys, values = extract_commands(conf)

        if "kubelet" in keys:
            if '--read-only-port' in keys and values[keys.index('--read-only-port')] == "0":
                return CheckResult.PASSED
            return CheckResult.FAILED

        return CheckResult.PASSED


check = KubeletReadOnlyPort()

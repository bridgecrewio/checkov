
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class KubeletStreamingConnectionIdleTimeout(BaseK8Check):
    def __init__(self):
        # CIS-1.6 4.2.5
        id = "CKV_K8S_143"
        name = "Ensure that the --streaming-connection-idle-timeout argument is not set to 0"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if "command" in conf:
            if "kubelet" in conf["command"]:            
                if "--streaming-connection-idle-timeout=0" in conf["command"]:
                    return CheckResult.FAILED

        return CheckResult.PASSED


check =  KubeletStreamingConnectionIdleTimeout()

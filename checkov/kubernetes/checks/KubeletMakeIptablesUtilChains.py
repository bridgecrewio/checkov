
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class KubeletMakeIptablesUtilChains(BaseK8Check):
    def __init__(self):
        # CIS-1.6 4.2.7
        id = "CKV_K8S_145"
        name = "Ensure that the --make-iptables-util-chains argument is set to true"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if "command" in conf:
            if "kubelet" in conf["command"]:            
                if "--make-iptables-util-chains=true" not in conf["command"]:
                    return CheckResult.FAILED

        return CheckResult.PASSED


check =  KubeletMakeIptablesUtilChains()

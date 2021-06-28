from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check

class ApiServerKubeletHttps(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_71"
        name = "Ensure that the --kubelet-https argument is set to true"
        categories = [CheckCategories.KUBERNETES]
        supported_kind = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if conf.get("command") is not None:
            if "kube-apiserver" in conf["command"]:
                if "--kubelet-https=false" in conf["command"]:
                    return CheckResult.FAILED

        return CheckResult.PASSED

check = ApiServerKubeletHttps()

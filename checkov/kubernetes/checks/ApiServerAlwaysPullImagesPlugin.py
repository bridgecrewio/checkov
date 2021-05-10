from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check

class ApiServerAlwaysPullImagesPlugin(BaseK8Check):
    def __init__(self):
        id = "CKV_K8S_80"
        name = "Ensure that the admission control plugin AlwaysPullImages is set"
        categories = [CheckCategories.KUBERNETES]
        supported_entities = ['containers']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if "command" in conf:
            if "kube-apiserver" in conf["command"]:
                for cmd in conf["command"]:
                    if cmd == "--enable-admission-plugins":
                        return CheckResult.FAILED  
                    if "=" in cmd:
                        [field,value,*_] = cmd.split("=")
                        if field == "--enable-admission-plugins":
                            if "AlwaysPullImages" not in value:
                                return CheckResult.FAILED 

        return CheckResult.PASSED

check = ApiServerAlwaysPullImagesPlugin()

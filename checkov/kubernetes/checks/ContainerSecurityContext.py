
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class ContainerSecurityContext(BaseK8Check):

    def __init__(self):
        # CIS-1.5 5.7.3
        name = "Apply security context to your pods and containers"
        # Security context can be set at pod or container level.
        # Location: container .securityContext
        id = "CKV_K8S_30"
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}' if conf.get('name') else conf["parent"]

    def scan_spec_conf(self, conf):
        if "securityContext" in conf:
            if conf["securityContext"]:
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = ContainerSecurityContext()

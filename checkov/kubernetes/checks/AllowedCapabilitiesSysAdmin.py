from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class AllowedCapabilitiesSysAdmin(BaseK8Check):

    def __init__(self):
        name = "Do not use the CAP_SYS_ADMIN linux capability"
        # This provides the most privilege and is similar to root
        # https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
        id = "CKV_K8S_39"
        # Location: container .spec.allowedCapabilities
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if "securityContext" in conf:
            if "capabilities" in conf["securityContext"]:
                if "add" in conf["securityContext"]["capabilities"]:
                    if "SYS_ADMIN" in conf["securityContext"]["capabilities"]["add"]:
                        return CheckResult.FAILED
        return CheckResult.PASSED


check = AllowedCapabilitiesSysAdmin()

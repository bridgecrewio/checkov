from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.base_spec_check import BaseK8Check


class ReadOnlyFilesystem(BaseK8Check):

    def __init__(self):
        name = "Use read-only filesystem for containers where possible"
        id = "CKV_K8S_22"
        # Location: container .securityContext.readOnlyRootFilesystem
        supported_kind = ['containers', 'initContainers']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_resource_id(self, conf):
        return f'{conf["parent"]} - {conf["name"]}'

    def scan_spec_conf(self, conf):
        if "securityContext" in conf:
            if "readOnlyRootFilesystem" in conf["securityContext"]:
                if conf["securityContext"]["readOnlyRootFilesystem"]:
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = ReadOnlyFilesystem()

from checkov.common.models.enums import CheckCategories
from checkov.kubernetes.checks.resource.base_spec_omitted_or_value_check import BaseSpecOmittedOrValueCheck


class ShareHostIPCPSP(BaseSpecOmittedOrValueCheck):

    def __init__(self):
        # CIS-1.3 1.7.3
        # CIS-1.5 5.2.3
        name = "Do not admit containers wishing to share the host IPC namespace"
        id = "CKV_K8S_3"
        # Location: PodSecurityPolicy.spec.hostIPC
        supported_kind = ['PodSecurityPolicy']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_inspected_key(self):
        return "spec/hostIPC"


check = ShareHostIPCPSP()

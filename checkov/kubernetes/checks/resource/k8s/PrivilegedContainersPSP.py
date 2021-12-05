from checkov.common.models.enums import CheckCategories
from checkov.kubernetes.checks.resource.base_spec_omitted_or_value_check import BaseSpecOmittedOrValueCheck


class PrivilegedContainersPSP(BaseSpecOmittedOrValueCheck):

    def __init__(self):
        # CIS-1.3 1.7.1
        # CIS-1.5 5.2.1
        name = "Do not admit privileged containers"
        id = "CKV_K8S_2"
        # Location: PodSecurityPolicy.spec.privileged
        supported_kind = ['PodSecurityPolicy']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_inspected_key(self):
        return "spec/privileged"


check = PrivilegedContainersPSP()

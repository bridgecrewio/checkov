from checkov.common.models.enums import CheckCategories
from checkov.kubernetes.base_spec_omitted_or_value_check import BaseSpecOmittedOrValueCheck


class AllowPrivilegeEscalation(BaseSpecOmittedOrValueCheck):

    def __init__(self):
        # CIS-1.3 1.7.5
        name = "Do not admit containers with allowPrivilegeEscalation"
        id = "CKV_K8S_5"
        supported_kind = ['PodSecurityPolicy']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_inspected_key(self):
        return "spec/allowPrivilegeEscalation"

    def get_resource_id(self, conf):
        return 'PodSecurityPolicy.spec.allowPrivilegeEscalation'


check = AllowPrivilegeEscalation()

from checkov.common.models.enums import CheckCategories
from checkov.kubernetes.checks.resource.base_spec_omitted_or_value_check import BaseSpecOmittedOrValueCheck


class SharedHostNetworkNamespacePSP(BaseSpecOmittedOrValueCheck):
    def __init__(self) -> None:
        # CIS-1.3 1.7.4
        # CIS-1.5 5.2.4
        name = "Do not admit containers wishing to share the host network namespace"
        id = "CKV_K8S_4"
        # Location: PodSecurityPolicy.spec.hostNetwork
        supported_kind = ("PodSecurityPolicy",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def get_inspected_key(self) -> str:
        return "spec/hostNetwork"


check = SharedHostNetworkNamespacePSP()

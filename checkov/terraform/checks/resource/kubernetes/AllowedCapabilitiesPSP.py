from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from typing import Any, List


class AllowedCapabilitiesPSP(BaseResourceNegativeValueCheck):

    def __init__(self):
        # CIS-1.5 5.2.8
        name = "Do not allow containers with added capability"
        # No capabilities may be added beyond the default set
        # https://kubernetes.io/docs/concepts/policy/pod-security-policy/#capabilities
        # Location: PodSecurityPolicy.spec.allowedCapabilities
        id = "CKV_K8S_24"
        supported_resources = ['kubernetes_pod_security_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'spec/[0]/allowed_capabilities'

    def get_forbidden_values(self) -> List[Any]:
        return [ANY_VALUE]


check = AllowedCapabilitiesPSP()

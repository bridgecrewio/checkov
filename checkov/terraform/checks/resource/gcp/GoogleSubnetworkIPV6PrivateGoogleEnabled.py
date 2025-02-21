from typing import Any, List, Dict

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck

# private_ip_google_access is not supported for subnetworks with the following purpose set
PURPOSE_EXCEPTIONS = ["INTERNAL_HTTPS_LOAD_BALANCER", "REGIONAL_MANAGED_PROXY", "GLOBAL_MANAGED_PROXY"]


class GoogleSubnetworkIPV6PrivateGoogleEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Private google access is enabled for IPV6"
        id = "CKV_GCP_76"
        supported_resources = ("google_compute_subnetwork",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        purpose = conf.get("purpose")
        if purpose and isinstance(purpose, list) and purpose[0] in PURPOSE_EXCEPTIONS:
            return CheckResult.UNKNOWN

        stack = conf.get("stack_type")
        if not stack or (stack and isinstance(stack, list) and stack[0] != "IPV4_IPV6"):
            return CheckResult.UNKNOWN

        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "private_ipv6_google_access"

    def get_expected_values(self) -> List[Any]:
        return ["ENABLE_OUTBOUND_VM_ACCESS_TO_GOOGLE", "ENABLE_BIDIRECTIONAL_ACCESS_TO_GOOGLE"]


check = GoogleSubnetworkIPV6PrivateGoogleEnabled()

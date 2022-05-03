from typing import Any, List, Dict

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GoogleSubnetworkLoggingEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Private google access is enabled for IPV6"
        id = "CKV_GCP_76"
        supported_resources = ("google_compute_subnetwork",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:

        stack = conf.get("stack_type")
        if stack and stack[0] != "IPV4_IPV6":
            return CheckResult.UNKNOWN

        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "private_ipv6_google_access"


check = GoogleSubnetworkLoggingEnabled()

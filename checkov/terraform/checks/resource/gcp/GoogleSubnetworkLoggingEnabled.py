from typing import Any, List, Dict

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck

# Only workload subnets carry VM traffic worth logging. Proxy-only subnets don't support
# flow logs; PSC and PRIVATE_NAT subnets host no VMs, so flow logs would capture nothing.
ENFORCEABLE_PURPOSES = ("PRIVATE", "PRIVATE_RFC_1918")


class GoogleSubnetworkLoggingEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that VPC Flow Logs is enabled for every subnet in a VPC Network"
        id = "CKV_GCP_26"
        supported_resources = ("google_compute_subnetwork",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        purpose = conf.get("purpose")

        if purpose and purpose[0] and purpose[0] not in ENFORCEABLE_PURPOSES:
            return CheckResult.UNKNOWN

        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "log_config"

    def get_expected_values(self) -> List[Any]:
        return [ANY_VALUE]


check = GoogleSubnetworkLoggingEnabled()

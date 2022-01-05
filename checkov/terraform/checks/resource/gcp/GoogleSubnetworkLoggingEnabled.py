from typing import Any, List, Dict

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GoogleSubnetworkLoggingEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that VPC Flow Logs is enabled for every subnet in a VPC Network"
        id = "CKV_GCP_26"
        supported_resources = ("google_compute_subnetwork",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        # flow logs can't be enabled for `INTERNAL_HTTPS_LOAD_BALANCER` subnetworks
        purpose = conf.get("purpose")
        if purpose and purpose[0] == "INTERNAL_HTTPS_LOAD_BALANCER":
            return CheckResult.UNKNOWN

        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "log_config"

    def get_expected_values(self) -> List[Any]:
        return [ANY_VALUE]


check = GoogleSubnetworkLoggingEnabled()

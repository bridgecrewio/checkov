from typing import Any, List, Dict

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck

# flow logs can't be enabled for subnetworks with the following purpose set
PURPOSE_EXCEPTIONS = ["INTERNAL_HTTPS_LOAD_BALANCER", "REGIONAL_MANAGED_PROXY", "GLOBAL_MANAGED_PROXY"]


class GoogleSubnetworkLoggingEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that VPC Flow Logs is enabled for every subnet in a VPC Network"
        id = "CKV_GCP_26"
        supported_resources = ("google_compute_subnetwork",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        purpose = conf.get("purpose")
        if purpose and purpose[0] in PURPOSE_EXCEPTIONS:
            return CheckResult.UNKNOWN

        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "log_config"

    def get_expected_values(self) -> List[Any]:
        return [ANY_VALUE]


check = GoogleSubnetworkLoggingEnabled()

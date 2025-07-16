from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck

# private_ip_google_access is not supported for subnetworks with the following purpose set
PURPOSE_EXCEPTIONS = ["INTERNAL_HTTPS_LOAD_BALANCER", "REGIONAL_MANAGED_PROXY", "GLOBAL_MANAGED_PROXY"]


class GoogleSubnetworkPrivateGoogleEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that private_ip_google_access is enabled for Subnet"
        id = "CKV_GCP_74"
        supported_resources = ("google_compute_subnetwork",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        purpose = conf.get("purpose")
        if purpose and isinstance(purpose, list) and purpose[0] in PURPOSE_EXCEPTIONS:
            return CheckResult.UNKNOWN

        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "private_ip_google_access"


check = GoogleSubnetworkPrivateGoogleEnabled()

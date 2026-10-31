from typing import List, Dict, Any
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GateProveEvidenceFreshness(BaseResourceCheck):
    """
    Ensures continuous drift monitoring and evidence freshness tracking are configured
    for SOC 2 Type II (CC6.8, CC7.1) and ISO 27001 (A.12.1.2) compliance.
    """

    def __init__(self) -> None:
        name = "Ensure continuous drift monitoring and evidence freshness tracking are configured (Gate/Prove)"
        id = "CKV_AWS_399"
        supported_resources = ["aws_config_configuration_recorder", "aws_config_delivery_channel"]
        categories = [CheckCategories.GENERAL_SECURITY, CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """
        Validates that recording_group captures all supported resource types
        or delivery frequency is configured to ensure continuous compliance evidence freshness.
        """
        # 1. Configuration Recorder check
        if "recording_group" in conf:
            rec_group = conf.get("recording_group", [{}])[0]
            if isinstance(rec_group, dict):
                # all_supported: true
                if rec_group.get("all_supported", [False])[0] is True:
                    return CheckResult.PASSED
                # include_global_resource_types: true
                if rec_group.get("include_global_resource_types", [False])[0] is True:
                    return CheckResult.PASSED

        # 2. Delivery Channel snapshot frequency check
        if "snapshot_delivery_properties" in conf:
            delivery_props = conf.get("snapshot_delivery_properties", [{}])[0]
            if isinstance(delivery_props, dict):
                freq = delivery_props.get("delivery_frequency", [""])[0]
                if freq in ["One_Hour", "Three_Hours", "Six_Hours", "Twelve_Hours", "TwentyFour_Hours"]:
                    return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["recording_group/[0]/all_supported", "snapshot_delivery_properties/[0]/delivery_frequency"]


check = GateProveEvidenceFreshness()

from __future__ import annotations

from typing import Any

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.data_structures_utils import find_in_dict


class IMDSv1Disabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Instance Metadata Service Version 1 is not enabled"
        id = "CKV_AWS_79"
        supported_resources = ("AWS::EC2::LaunchTemplate",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        # IMDS can be disabled or IMDSv2 can be enabled
        http_endpoint = find_in_dict(
            input_dict=conf,
            key_path="Properties/LaunchTemplateData/MetadataOptions/HttpEndpoint",
        )
        if http_endpoint == "disabled":
            return CheckResult.PASSED

        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "Properties/LaunchTemplateData/MetadataOptions/HttpTokens"

    def get_expected_value(self) -> Any:
        return "required"


check = IMDSv1Disabled()

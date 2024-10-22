from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class IMDSv1Disabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Instance Metadata Service Version 1 is not enabled"
        id = "CKV_AWS_79"
        categories = (CheckCategories.GENERAL_SECURITY,)
        supported_resources = ("aws_instance", "aws_launch_template", "aws_launch_configuration")
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        """
        Looks for if the metadata service is disabled or requires session tokens:
        https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#metadata-options
        or
        https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/launch_template#metadata-options

        :param conf: dict of supported resource configuration
        :return: <CheckResult>
        """
        metadata_options = conf.get("metadata_options")
        if not metadata_options or not isinstance(metadata_options[0], dict):
            return CheckResult.FAILED

        if metadata_options[0].get("http_endpoint") == ["disabled"]:
            return CheckResult.PASSED

        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "metadata_options/[0]/http_tokens"

    def get_expected_value(self) -> Any:
        return "required"


check = IMDSv1Disabled()

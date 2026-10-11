from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AthenaWorkgroupEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Athena Workgroup is encrypted"
        id = "CKV_AWS_159"
        supported_resources = ("aws_athena_workgroup",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        configuration = conf.get("configuration", [])
        if configuration and isinstance(configuration[0], dict):
            managed_results = configuration[0].get("managed_query_results_configuration", [])
            if managed_results and isinstance(managed_results[0], dict) and managed_results[0].get("enabled") == [True]:
                return CheckResult.PASSED
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "configuration/[0]/result_configuration/[0]/encryption_configuration/[0]/encryption_option"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AthenaWorkgroupEncryption()

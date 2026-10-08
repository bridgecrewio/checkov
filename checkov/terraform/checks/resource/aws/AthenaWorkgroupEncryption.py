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
        # Managed query results are always encrypted at rest, with an AWS owned key unless a KMS key is set:
        # https://docs.aws.amazon.com/athena/latest/ug/managed-results.html#managed-query-results-encryption-at-rest
        # result_configuration.output_location can't be set in this mode, so the key below is never present.
        configuration = conf.get("configuration")
        if configuration and isinstance(configuration[0], dict):
            managed_results = configuration[0].get("managed_query_results_configuration")
            if managed_results and isinstance(managed_results[0], dict):
                if managed_results[0].get("enabled") in ([True], ["true"]):
                    self.evaluated_keys = ["configuration/[0]/managed_query_results_configuration/[0]/enabled"]
                    return CheckResult.PASSED

        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "configuration/[0]/result_configuration/[0]/encryption_configuration/[0]/encryption_option"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AthenaWorkgroupEncryption()

from typing import List

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.parsers.node import DictNode
from checkov.common.models.enums import CheckResult, CheckCategories


class NeptuneClusterLogging(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Neptune logging is enabled"
        id = "CKV_AWS_101"
        supported_resources = ["AWS::Neptune::DBCluster"]
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: DictNode) -> CheckResult:
        log_types = ["audit"]

        logs_exports = conf.get("Properties", {}).get("EnableCloudwatchLogsExports", [])
        if all(elem in logs_exports for elem in log_types):
            return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["Properties/EnableCloudwatchLogsExports"]

check = NeptuneClusterLogging()

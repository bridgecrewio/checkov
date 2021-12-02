from typing import List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class DocDBLogging(BaseResourceCheck):
    def __init__(self):
        name = "Ensure DocDB Logging is enabled"
        id = "CKV_AWS_85"
        supported_resources = ['AWS::DocDB::DBCluster']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        log_types = ["profiler", "audit"]
        if 'Properties' in conf.keys():
            if 'EnableCloudwatchLogsExports' in conf['Properties'].keys():
                if all(elem in conf['Properties']['EnableCloudwatchLogsExports'] for elem in log_types):
                    return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["Properties/EnableCloudwatchLogsExports"]


check = DocDBLogging()

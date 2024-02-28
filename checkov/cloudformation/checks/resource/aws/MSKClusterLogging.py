from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class MSKClusterLogging(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure MSK Cluster logging is enabled"
        id = "CKV_AWS_80"
        supported_resources = ['AWS::MSK::Cluster']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> Any:
        if 'Properties' in conf.keys():
            if 'LoggingInfo' in conf['Properties'].keys():
                if 'BrokerLogs' in conf['Properties']['LoggingInfo'].keys():
                    logging = conf['Properties']['LoggingInfo']['BrokerLogs']
                    types = ["CloudWatchLogs", "Firehose", "S3"]
                    for x in types:
                        if x in logging and 'Enabled' in logging[x] and logging[x]['Enabled'] is True:
                            return CheckResult.PASSED
        return CheckResult.FAILED


check = MSKClusterLogging()

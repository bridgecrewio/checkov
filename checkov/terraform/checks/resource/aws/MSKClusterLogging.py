from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class MSKClusterLogging(BaseResourceCheck):
    def __init__(self):
        name = "Ensure MSK Cluster logging is enabled"
        id = "CKV_AWS_80"
        supported_resources = ['aws_msk_cluster']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'logging_info' in conf.keys() and 'broker_logs' in conf['logging_info'][0]:
            logging = conf['logging_info'][0]['broker_logs'][0]
            types = ["cloudwatch_logs", "firehose", "s3"]
            for x in types:
                if x in logging and logging[x][0]['enabled'] is True:
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = MSKClusterLogging()

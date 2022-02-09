import json
import logging

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class BatchJobIsNotPrivileged(BaseResourceCheck):
    def __init__(self):
        name = "Batch job does not define a privileged container"
        id = "CKV_AWS_210"
        supported_resources = ['aws_batch_job_definition']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("container_properties"):
            if type(conf.get("container_properties")[0]) is str:
                try:
                    container = json.loads(conf.get("container_properties")[0])
                except json.JSONDecodeError as e:
                    logging.error(e)
                    return CheckResult.UNKNOWN
            else:
                container = conf.get("container_properties")[0]
            if container.get("privileged"):
                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = BatchJobIsNotPrivileged()

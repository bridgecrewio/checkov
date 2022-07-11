from checkov.common.models.enums import CheckCategories,CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RDSInstanceLogsEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure RDS Instance Parameters are set to enable logging"
        id = "CKV_ALI_35"
        supported_resources = ['alicloud_db_instance']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("parameters") and isinstance(conf.get("parameters"), list):
            params = conf.get("parameters")
            for param in params:
                if param['name'][0] == "log_duration" and param['value'][0] == 'ON':
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = RDSInstanceLogsEnabled()

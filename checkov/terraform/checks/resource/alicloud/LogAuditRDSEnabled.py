from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class LogAuditRDSEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure log audit is enabled for RDS"
        id = "CKV_ALI_38"
        supported_resources = ['alicloud_log_audit']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('variable_map') and isinstance(conf.get('variable_map'), list):
            settings = conf.get('variable_map')[0]
            if settings.get('rds_enabled'):
                return CheckResult.PASSED
        self.evaluated_keys = ['variable_map/rds_enabled']
        return CheckResult.FAILED


check = LogAuditRDSEnabled()

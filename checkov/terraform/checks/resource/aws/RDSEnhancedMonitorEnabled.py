from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RDSEnhancedMonitorEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that enhanced monitoring is enabled for Amazon RDS instances"
        id = "CKV_AWS_118"
        supported_resources = ['aws_db_instance', 'aws_rds_cluster_instance']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'monitoring_interval'

    def get_expected_values(self):
        return [1, 5, 10, 15, 30, 60]


check = RDSEnhancedMonitorEnabled()

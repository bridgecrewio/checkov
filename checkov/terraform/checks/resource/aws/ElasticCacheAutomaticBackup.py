from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class ElasticCacheAutomaticBackup(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that Amazon ElastiCache Redis clusters have automatic backup turned on"
        id = "CKV_AWS_134"
        supported_resources = ['aws_elasticache_cluster']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_attribute_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return 'snapshot_retention_limit'

    def get_forbidden_values(self):
        return [0]


check = ElasticCacheAutomaticBackup()

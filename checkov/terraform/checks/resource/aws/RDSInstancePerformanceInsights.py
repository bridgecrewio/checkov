from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class RDSInstancePerformanceInsights(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that RDS instances have performance insights enabled"
        id = "CKV_AWS_353"
        supported_resources = ('aws_rds_cluster_instance', 'aws_db_instance')
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'performance_insights_enabled'


check = RDSInstancePerformanceInsights()

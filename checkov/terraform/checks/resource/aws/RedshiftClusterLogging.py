from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RedshiftClusterLogging(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Redshift Cluster logging is enabled"
        id = "CKV_AWS_71"
        supported_resource = ['aws_redshift_cluster']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def get_inspected_key(self):
        return 'logging/[0]/enable'

check = RedshiftClusterLogging()

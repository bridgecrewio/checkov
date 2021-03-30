from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class RDSEnableIAMAuthentication(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that an Amazon RDS Clusters have AWS Identity and Access Management (IAM) authentication enabled"
        id = "CKV_AWS_128"
        supported_resources = ['aws_rds_cluster']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'iam_database_authentication_enabled'


check = RDSEnableIAMAuthentication()

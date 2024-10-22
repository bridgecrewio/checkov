from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class NeptuneDBClustersIAMDatabaseAuthenticationEnabled(BaseResourceValueCheck):
    def __init__(self):
        description = "Neptune DB clusters should have IAM database authentication enabled"
        id = "CKV_AWS_359"
        supported_resources = ['aws_neptune_cluster']
        categories = [CheckCategories.IAM]
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "iam_database_authentication_enabled"


check = NeptuneDBClustersIAMDatabaseAuthenticationEnabled()

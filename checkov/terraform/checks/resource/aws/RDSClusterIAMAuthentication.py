from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class RDSClusterIAMAuthentication(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure RDS cluster has IAM authentication enabled"
        id = "CKV_AWS_162"
        supported_resources = ["aws_rds_cluster"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "iam_database_authentication_enabled"


check = RDSClusterIAMAuthentication()

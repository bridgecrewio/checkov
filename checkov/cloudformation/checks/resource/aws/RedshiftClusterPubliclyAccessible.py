from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class RedshiftClusterPubliclyAccessible(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Redshift cluster should not be publicly accessible"
        id = "CKV_AWS_87"
        supported_resources = ["AWS::Redshift::Cluster"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/PubliclyAccessible"

    def get_expected_value(self):
        return False


check = RedshiftClusterPubliclyAccessible()

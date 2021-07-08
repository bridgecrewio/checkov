from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories


class RedshiftClusterLogging(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Redshift Cluster logging is enabled"
        id = "CKV_AWS_71"
        supported_resources = ["AWS::Redshift::Cluster"]
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/LoggingProperties/BucketName"

    def get_expected_value(self) -> str:
        return ANY_VALUE


check = RedshiftClusterLogging()

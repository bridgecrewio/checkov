from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories


class RedshiftInEc2ClassicMode(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Redshift is not deployed outside of a VPC"
        id = "CKV_AWS_154"
        supported_resources = ["AWS::Redshift::Cluster"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/ClusterSubnetGroupName"

    def get_expected_value(self) -> str:
        return ANY_VALUE


check = RedshiftInEc2ClassicMode()

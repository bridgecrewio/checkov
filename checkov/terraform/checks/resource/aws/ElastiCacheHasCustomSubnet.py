from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ElastiCacheHasCustomSubnet(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        NIST.800-53.r5 AC-4, NIST.800-53.r5 AC-4(21), NIST.800-53.r5 SC-7, NIST.800-53.r5 SC-7(11),
        NIST.800-53.r5 SC-7(16), NIST.800-53.r5 SC-7(21), NIST.800-53.r5 SC-7(4), NIST.800-53.r5 SC-7(5)
        ElastiCache clusters should not use the default subnet group
        """
        name = "Ensure ElastiCache clusters do not use the default subnet group"
        id = "CKV_AWS_323"
        supported_resources = ("aws_elasticache_cluster",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "subnet_group_name"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = ElastiCacheHasCustomSubnet()

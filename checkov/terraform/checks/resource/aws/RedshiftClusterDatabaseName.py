from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.models.consts import ANY_VALUE
from typing import Any


class RedshiftClusterDatabaseName(BaseResourceValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 CA-9(1), NIST.800-53.r5 CM-2
        Redshift clusters should not use the default database name
        """
        name = "Ensure Redshift clusters do not use the default database name"
        id = "CKV_AWS_320"
        supported_resources = ('aws_redshift_cluster',)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return "database_name"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = RedshiftClusterDatabaseName()

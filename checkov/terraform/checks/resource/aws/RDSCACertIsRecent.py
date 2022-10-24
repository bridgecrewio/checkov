from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any, List


class RDSCACertIsRecent(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure RDS uses a modern CaCert"
        id = "CKV_AWS_211"
        supported_resources = ["aws_db_instance"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.PASSED
        )

    def get_inspected_key(self) -> str:
        return "ca_cert_identifier"

    def get_expected_values(self) -> List[Any]:
        return ["rds-ca-2019"]


check = RDSCACertIsRecent()

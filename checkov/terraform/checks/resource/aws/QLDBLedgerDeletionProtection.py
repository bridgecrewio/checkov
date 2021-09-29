from typing import Dict, List, Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class QLDBLedgerDeletionProtection(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure QLDB ledger has deletion protection enabled"
        id = "CKV_AWS_172"
        supported_resources = ["aws_qldb_ledger"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "deletion_protection"


check = QLDBLedgerDeletionProtection()

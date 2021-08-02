from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class QLDBLedgerPermissionsMode(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure QLDB ledger permissions mode is set to STANDARD"
        id = "CKV_AWS_170"
        supported_resources = ["aws_qldb_ledger"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "permissions_mode"

    def get_expected_value(self) -> str:
        return "STANDARD"


check = QLDBLedgerPermissionsMode()

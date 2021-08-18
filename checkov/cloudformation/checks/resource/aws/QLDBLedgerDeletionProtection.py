from typing import Dict

from checkov.cloudformation.parser.node import str_node, dict_node
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class QLDBLedgerDeletionProtection(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure QLDB ledger has deletion protection enabled"
        id = "CKV_AWS_172"
        supported_resources = ["AWS::QLDB::Ledger"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str_node, dict_node]) -> CheckResult:
        # deletion protection is enabled on default
        if "DeletionProtection" not in conf.get("Properties", {}):
            return CheckResult.PASSED
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "Properties/DeletionProtection"


check = QLDBLedgerDeletionProtection()

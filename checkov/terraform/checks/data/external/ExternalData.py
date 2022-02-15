from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.data.base_check import BaseDataCheck


class ExternalData(BaseDataCheck):
    def __init__(self) -> None:
        name = 'Ensure terraform external data blocks runs vetted code'
        id = "CKV_TF_DATA_EXTERNAL_1"
        supported_data = ["external"]
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(name=name, id=id, categories=categories, supported_data=supported_data)

    def scan_data_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        # based on https://hackingthe.cloud/terraform/terraform_enterprise_metadata_service/
        return CheckResult.FAILED


check = ExternalData()

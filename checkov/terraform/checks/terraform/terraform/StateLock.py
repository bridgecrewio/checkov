from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.terraform.base_check import BaseTerraformBlockCheck


class StateLock(BaseTerraformBlockCheck):
    def __init__(self) -> None:
        name = "Ensure state files are locked"
        id = "CKV_TF_3"
        supported_blocks = ("terraform",)
        categories = (CheckCategories.SUPPLY_CHAIN,)
        super().__init__(name=name, id=id, categories=categories, supported_blocks=supported_blocks)

    def scan_terraform_block_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        # see: https://developer.hashicorp.com/terraform/language/terraform
        if "backend" not in conf:
            return CheckResult.UNKNOWN

        backend = conf["backend"][0] if isinstance(conf["backend"], list) else conf["backend"]

        if "s3" not in backend:
            return CheckResult.UNKNOWN

        s3_config = backend["s3"]
        if ("use_lockfile" not in s3_config or not s3_config["use_lockfile"]) and "dynamodb_table" not in s3_config:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = StateLock()

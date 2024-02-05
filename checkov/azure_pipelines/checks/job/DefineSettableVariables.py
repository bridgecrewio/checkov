from __future__ import annotations

from typing import Any

from checkov.azure_pipelines.checks.base_azure_pipelines_check import BaseAzurePipelinesCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.yaml_doc.enums import BlockType


class DefineSettableVariables(BaseAzurePipelinesCheck):
    def __init__(self) -> None:
        name = "Ensure a task enforces settableVariables to prevent malicious user input overriding system vars."
        id = "CKV_AZUREPIPELINES_4"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.SUPPLY_CHAIN,),
            supported_entities=("jobs[].steps[]", "stages[].jobs[].steps[]"),
            block_type=BlockType.ARRAY,
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        run_cmd = conf.get("bash") or conf.get("powershell")
        if run_cmd and isinstance(run_cmd, str):
            target_subsection = conf.get("target")
            if target_subsection:
                settableVariables_subsection = target_subsection.get("settableVariables")
                if settableVariables_subsection:
                    return CheckResult.PASSED, conf

            return CheckResult.FAILED, conf

        else:
            return CheckResult.UNKNOWN, conf


check = DefineSettableVariables()

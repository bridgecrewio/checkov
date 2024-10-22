from __future__ import annotations

from typing import Any

from checkov.azure_pipelines.checks.base_azure_pipelines_check import BaseAzurePipelinesCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.yaml_doc.enums import BlockType


class SetSecretVariable(BaseAzurePipelinesCheck):
    def __init__(self) -> None:
        name = "Ensure set variable is not marked as a secret"
        id = "CKV_AZUREPIPELINES_3"
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
            variable_found = False

            for line in run_cmd.splitlines():
                if "task.setvariable" in line:
                    variable_found = True

                    if "issecret=true" in line:
                        return CheckResult.FAILED, conf

            if variable_found:
                # should only pass, if it really found a set variable, otherwise unknown
                return CheckResult.PASSED, conf

        return CheckResult.UNKNOWN, conf


check = SetSecretVariable()

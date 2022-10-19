from __future__ import annotations

from typing import Any

from checkov.azure_pipelines.checks.base_azure_pipelines_check import BaseAzurePipelinesCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.yaml_doc.enums import BlockType


class ContainerDigest(BaseAzurePipelinesCheck):
    def __init__(self) -> None:
        name = "Ensure container job uses a version digest"
        id = "CKV_AZUREPIPELINES_2"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.SUPPLY_CHAIN,),
            supported_entities=("jobs", "stages[].jobs[]"),
            block_type=BlockType.ARRAY,
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        container = conf.get("container")
        if container and isinstance(container, str):
            if "@" in container:
                return CheckResult.PASSED, conf

            return CheckResult.FAILED, conf

        return CheckResult.UNKNOWN, conf


check = ContainerDigest()

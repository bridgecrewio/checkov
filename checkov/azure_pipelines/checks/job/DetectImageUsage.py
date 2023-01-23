from __future__ import annotations

from typing import Any

from checkov.azure_pipelines.checks.base_azure_pipelines_check import BaseAzurePipelinesCheck
from checkov.common.models.enums import CheckResult
from checkov.yaml_doc.enums import BlockType


class DetectImageUsage(BaseAzurePipelinesCheck):
    def __init__(self) -> None:
        name = "Detecting image usages in azure pipelines workflows"
        id = "CKV_AZUREPIPELINES_4"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=('*.image[]', '*.vmImage[]', '*.container[]')
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        return CheckResult.PASSED, conf


check = DetectImageUsage()
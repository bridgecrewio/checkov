from __future__ import annotations
from typing import Any

from checkov.circleci_pipelines.base_circleci_pipelines_check import BaseCircleCIPipelinesCheck
from checkov.common.models.enums import CheckResult
from checkov.yaml_doc.enums import BlockType


class DetectImageUsage(BaseCircleCIPipelinesCheck):
    def __init__(self) -> None:
        name = "Detecting image usages in circleci pipelines"
        id = "CKV_CIRCLECIPIPELINES_8"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=(
                "executors.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}",
                "jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}",
            )
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        return CheckResult.PASSED, conf


check = DetectImageUsage()

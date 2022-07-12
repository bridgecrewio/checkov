from __future__ import annotations
from typing import Any

from checkov.circleci_pipelines.base_circleci_pipelines_check import BaseCircleCIPipelinesCheck
from checkov.common.models.enums import CheckResult
from checkov.yaml_doc.enums import BlockType


class ImageReferenceHashVersion(BaseCircleCIPipelinesCheck):
    def __init__(self) -> None:
        name = "Ensure the pipeline image version is referenced via hash not arbitrary tag."
        id = "CKV_CIRCLECIPIPELINES_2"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=['jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}']
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        if not isinstance(conf, dict):
            return CheckResult.PASSED, conf
        image = conf.get("image", None)
        if not image:
            return CheckResult.PASSED, conf
        if isinstance(image, str):
            if "@" in image:
                return CheckResult.PASSED, conf
            if "latest" in image:
                return CheckResult.UNKNOWN, conf
                # We UNKNOWN on "latest" as we have a specific check with a more informative violation description.
                # See CKV_CIRCLECIPIPELINES_1

        return CheckResult.FAILED, conf


check = ImageReferenceHashVersion()

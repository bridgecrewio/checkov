from __future__ import annotations

from typing import Any

from checkov.bitbucket_pipelines.base_bitbucket_pipelines_check import BaseBitbucketPipelinesCheck
from checkov.common.models.enums import CheckResult
from checkov.yaml_doc.enums import BlockType


class ImageReferenceLatestTag(BaseBitbucketPipelinesCheck):
    def __init__(self) -> None:
        name = "Ensure the pipeline image uses a non latest version tag"
        id = "CKV_BITBUCKETPIPELINES_1"
        super().__init__(
            name=name,
            id=id,
            block_type=BlockType.ARRAY,
            supported_entities=(
                "[{image:image,__startline__:__startline__,__endline__:__endline__}]",
                "pipelines.default[].step.{image: image, __startline__: __startline__, __endline__:__endline__}",
                "pipelines.*.[*][][][].step.{image: image, __startline__: __startline__, __endline__:__endline__}",
            ),
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        if not isinstance(conf, dict):
            return CheckResult.UNKNOWN, conf
        image = conf.get("image")
        if not image:
            return CheckResult.UNKNOWN, conf
        if isinstance(image, str):
            if image.endswith(":latest"):
                return CheckResult.FAILED, conf

        return CheckResult.PASSED, conf


check = ImageReferenceLatestTag()

from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction


class MaintainerExists(BaseDockerfileCheck):
    def __init__(self) -> None:
        name = "Ensure that LABEL maintainer is used instead of MAINTAINER (deprecated)"
        id = "CKV_DOCKER_6"
        supported_instructions = ("MAINTAINER",)
        categories = (CheckCategories.CONVENTION,)
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_resource_conf(self, conf: list[_Instruction]) -> tuple[CheckResult, list[_Instruction] | None]:
        return CheckResult.FAILED, conf


check = MaintainerExists()

from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction


class HealthcheckExists(BaseDockerfileCheck):
    def __init__(self) -> None:
        name = "Ensure that HEALTHCHECK instructions have been added to container images"
        id = "CKV_DOCKER_2"
        supported_instructions = ("*",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_resource_conf(self, conf: dict[str, list[_Instruction]]) -> tuple[CheckResult, list[_Instruction] | None]:  # type:ignore[override]  # special wildcard behaviour
        for instruction, content in conf.items():
            if instruction == "HEALTHCHECK":
                return CheckResult.PASSED, content
        return CheckResult.FAILED, None


check = HealthcheckExists()

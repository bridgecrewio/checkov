from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction


class ExposePort22(BaseDockerfileCheck):
    def __init__(self) -> None:
        name = "Ensure port 22 is not exposed"
        id = "CKV_DOCKER_1"
        supported_instructions = ("EXPOSE",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_resource_conf(self, conf: list[_Instruction]) -> tuple[CheckResult, list[_Instruction] | None]:
        for expose in conf:
            if any(port in expose["value"].split(" ") for port in ("22", "22/tcp")):
                return CheckResult.FAILED, [expose]

        return CheckResult.PASSED, None


check = ExposePort22()

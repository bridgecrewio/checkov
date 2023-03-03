from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction


class AddExists(BaseDockerfileCheck):
    def __init__(self) -> None:
        name = "Ensure that COPY is used instead of ADD in Dockerfiles"
        id = "CKV_DOCKER_4"
        supported_instructions = ("ADD",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_resource_conf(self, conf: list[_Instruction]) -> tuple[CheckResult, list[_Instruction] | None]:
        for instruction in conf:
            if instruction['instruction'] == "ADD":
                return CheckResult.FAILED, conf
        return CheckResult.PASSED, None


check = AddExists()

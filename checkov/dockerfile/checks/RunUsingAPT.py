from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction


class RunUsingAPT(BaseDockerfileCheck):
    def __init__(self) -> None:
        """
        Apt interface is less stable than apt-get and so this preferred
        """
        name = "Ensure that APT isn't used"
        id = "CKV_DOCKER_9"
        supported_instructions = ("RUN",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_resource_conf(self, conf: list[_Instruction]) -> tuple[CheckResult, list[_Instruction] | None]:
        for run in conf:
            content = run["content"]
            if " apt " in content:
                return CheckResult.FAILED, [run]
        return CheckResult.PASSED, None


check = RunUsingAPT()

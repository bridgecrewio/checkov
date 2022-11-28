from __future__ import annotations

import re
from typing import TYPE_CHECKING

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction

ISABSOLUTE = re.compile('^"?((/[A-Za-z0-9-_+]*)|([A-Za-z0-9-_+]:\\\\.*)|(\\$[{}A-Za-z0-9-_+].*))')


class WorkdirIsAbsolute(BaseDockerfileCheck):
    def __init__(self) -> None:
        """
        For clarity and reliability, you should always use absolute paths for your WORKDIR.
        """
        name = "Ensure that WORKDIR values are absolute paths"
        id = "CKV_DOCKER_10"
        supported_instructions = ("WORKDIR",)
        categories = (CheckCategories.CONVENTION,)
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_resource_conf(self, conf: list[_Instruction]) -> tuple[CheckResult, list[_Instruction] | None]:
        workdirs = []
        for workdir in conf:
            path = workdir["value"]
            if isinstance(path, str) and not re.match(ISABSOLUTE, path):
                workdirs.append(workdir)

        if workdirs:
            return CheckResult.FAILED, workdirs

        return CheckResult.PASSED, None


check = WorkdirIsAbsolute()

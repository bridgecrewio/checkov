from __future__ import annotations

import re

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck

ISABSOLUTE = re.compile("(^/[A-z0-9-_+]*)|(^[A-z0-9-_+]:\\\\.*)|(^\\$[{}A-z0-9-_+].*)")


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

    def scan_entity_conf(self, conf: list[dict[str, int | str]]) -> tuple[CheckResult, list[dict[str, int | str]] | None]:
        workdirs = []
        for workdir in conf:
            path = workdir["value"]
            if not re.match(ISABSOLUTE, path):
                workdirs.append(workdir)

        if workdirs:
            return CheckResult.FAILED, workdirs

        return CheckResult.PASSED, None


check = WorkdirIsAbsolute()

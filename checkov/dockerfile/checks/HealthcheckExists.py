from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck


class HealthcheckExists(BaseDockerfileCheck):
    def __init__(self) -> None:
        name = "Ensure that HEALTHCHECK instructions have been added to container images"
        id = "CKV_DOCKER_2"
        supported_instructions = ("*",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_entity_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any] | None]:
        for instruction, content in conf.items():
            if instruction == "HEALTHCHECK":
                return CheckResult.PASSED, content[0]
        return CheckResult.FAILED, None


check = HealthcheckExists()

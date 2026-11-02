from __future__ import annotations

import re
from typing import TYPE_CHECKING

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction

MULTI_STAGE_PATTERN = re.compile(r"(?:--platform=\S+\s+)?(\S+)\s+as\s+(\S+)", re.IGNORECASE)
ARG_REF_PATTERN = re.compile(r"^\$\{?(\w+)\}?$")


class ReferenceLatestTag(BaseDockerfileCheck):
    def __init__(self) -> None:
        name = "Ensure the base image uses a non latest version tag"
        id = "CKV_DOCKER_7"
        supported_instructions = ("*",)
        categories = (CheckCategories.CONVENTION,)
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_resource_conf(self, conf: dict[str, list[_Instruction]]) -> tuple[CheckResult, list[_Instruction] | None]:  # type:ignore[override]  # special wildcard behaviour
        stages = []
        arg_defaults: dict[str, str] = {}
        for arg in conf.get("ARG", []):
            arg_value = arg["value"]
            if "=" in arg_value:
                arg_name, _, arg_default = arg_value.partition("=")
                arg_defaults[arg_name.strip()] = arg_default.strip().strip('"').strip("'")

        for content in conf.get("FROM", []):
            base_image = content["value"]
            if " as " in base_image.lower():
                multi_stage = re.match(MULTI_STAGE_PATTERN, base_image)
                if multi_stage:
                    base_image = multi_stage[1]
                    stages.append(multi_stage[2])

            arg_ref = ARG_REF_PATTERN.match(base_image)
            if arg_ref and arg_ref.group(1) in arg_defaults:
                base_image = arg_defaults[arg_ref.group(1)]

            if ":" not in base_image and base_image not in stages and base_image != "scratch":
                return CheckResult.FAILED, [content]
            elif base_image.endswith(":latest"):
                return CheckResult.FAILED, [content]
        return CheckResult.PASSED, [content]


check = ReferenceLatestTag()
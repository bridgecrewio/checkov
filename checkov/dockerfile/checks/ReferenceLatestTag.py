import re

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck

MULTI_STAGE_PATTERN = re.compile(r"(\S+)\s+as\s+(\S+)")


class ReferenceLatestTag(BaseDockerfileCheck):
    def __init__(self):
        name = "Ensure the base image uses a non latest version tag"
        id = "CKV_DOCKER_7"
        supported_instructions = ["FROM"]
        categories = [CheckCategories.CONVENTION]
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_entity_conf(self, conf):
        stages = []

        for content in conf:
            base_image = content["value"]
            multi_stage = re.match(MULTI_STAGE_PATTERN, base_image)
            if multi_stage:
                base_image = multi_stage[1]
                stages.append(multi_stage[2])

            if ":" not in base_image and base_image not in stages:
                return CheckResult.FAILED, content
            elif base_image.endswith(":latest"):
                return CheckResult.FAILED, content
        return CheckResult.PASSED, None


check = ReferenceLatestTag()

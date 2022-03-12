
import collections

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck


class AliasIsUnique(BaseDockerfileCheck):
    def __init__(self):
        """
        Ensure From Alias are unique for multistage builds.
        """
        name = "Ensure From Alias are unique for multistage builds."
        id = "CKV_DOCKER_11"
        supported_instructions = ["FROM"]
        categories = [CheckCategories.CONVENTION]
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_entity_conf(self, conf):
        alias = []
        for instruction in conf:
            if " as " in instruction["value"]:
                temp = instruction["value"].split()
                alias += [temp[2]]

        if len(alias) == len(set(alias)):
            return CheckResult.PASSED, None
        else:
            return CheckResult.FAILED, conf[0]


check = AliasIsUnique()

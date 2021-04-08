from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck

install_commands = [
    "install",
    "source-install",
    "reinstall",
    "groupinstall",
    "localinstall",
    "add",
]
update_commands = [
    "update",
    "--update"
]


class UpdateNotAlone(BaseDockerfileCheck):
    def __init__(self):
        name = "Ensure update instructions are not use alone in the Dockerfile"
        id = "CKV_DOCKER_5"
        supported_instructions = ["RUN"]
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_entity_conf(self, conf):
        update_instruction = 0
        update_cnt = 0
        i = 0
        for instruction in conf:
            content = instruction['content']
            if instruction['instruction'] in self.supported_instructions:

                if any(x in content for x in update_commands):
                    update_cnt = update_cnt + 1
                    update_instruction = i
                if any(x in content for x in install_commands):
                    update_cnt = update_cnt - 1
            i = i + 1

        if update_cnt <= 0:
            return CheckResult.PASSED, None
        return CheckResult.FAILED, conf[update_instruction]


check = UpdateNotAlone()

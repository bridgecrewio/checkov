from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck


class UserExists(BaseDockerfileCheck):
    def __init__(self):
        name = "Ensure that a user for the container has been created"
        id = "CKV_DOCKER_3"
        supported_instructions = ["CMD", "ENTRYPOINT", "USER"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_entity_conf(self, conf):
        for instruction in conf:
            value = instruction['value']
            if instruction['instruction'] in self.supported_instructions:
                if instruction['instruction'] == "USER":
                    return CheckResult.PASSED, None
                elif instruction['instruction'] in ["CMD", "ENTRYPOINT"]:
                    if "gosu" in value:
                        if len(value) >= value.index("gosu")+3:
                            return CheckResult.PASSED, None


check = UserExists()

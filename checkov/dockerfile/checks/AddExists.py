from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck


class AddExists(BaseDockerfileCheck):
    def __init__(self):
        name = "Ensure that COPY is used instead of ADD in Dockerfiles"
        id = "CKV_DOCKER_4"
        supported_instructions = ["ADD"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_entity_conf(self, conf):
        i=0
        for instruction in conf:
            if instruction['instruction'] == "ADD":
                return CheckResult.FAILED, conf[i]
        return CheckResult.PASSED,None


check = AddExists()

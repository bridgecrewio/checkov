from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck


class SpecifyImageVersion(BaseDockerfileCheck):
    def __init__(self):
        name = "Ensure that Image version is specified"
        id = "CKV_DOCKER_10"
        supported_instructions = ["FROM"]
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_entity_conf(self, conf):
        content = conf[0]['content']
        if "scratch" in content:
            return CheckResult.PASSED, conf[0]
        if ":" in content:
            return CheckResult.PASSED, conf[0]
        return CheckResult.FAILED, None


check = SpecifyImageVersion()

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck


class RunUsingAPT(BaseDockerfileCheck):
    def __init__(self):
        """
        Apt interface is less stable than apt-get and so this preferred
        """
        name = "Ensure that APT isn't used"
        id = "CKV_DOCKER_9"
        supported_instructions = ["RUN"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_entity_conf(self, conf):
        for run in conf:
            content = run["content"]
            if " apt " in content:
                return CheckResult.FAILED, run
        return CheckResult.PASSED, None


check = RunUsingAPT()

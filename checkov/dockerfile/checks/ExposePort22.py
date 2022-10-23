from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck


class ExposePort22(BaseDockerfileCheck):
    def __init__(self):
        name = "Ensure port 22 is not exposed"
        id = "CKV_DOCKER_1"
        supported_instructions = ['EXPOSE']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_entity_conf(self, conf):
        i = 0
        for expose_term in conf:
            if "22" in expose_term['value'].split(' '):
                return CheckResult.FAILED, conf[i]
            i += 1
        return CheckResult.PASSED , None


check = ExposePort22()

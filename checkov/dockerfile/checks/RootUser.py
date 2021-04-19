from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck


class RootUser(BaseDockerfileCheck):
    def __init__(self):
        name = "Ensure the last USER is not root"
        id = "CKV_DOCKER_8"
        supported_instructions = ["USER"]
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_entity_conf(self, conf):
        last_user = conf[-1]
        if last_user["value"] == "root":
            return CheckResult.FAILED, last_user

        return CheckResult.PASSED, last_user


check = RootUser()

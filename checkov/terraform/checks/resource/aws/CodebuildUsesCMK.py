from typing import Dict, List, Any

from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class CodeBuildEncrypted(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that CodeBuild projects are encrypted using CMK"
        id = "CKV_AWS_147"
        supported_resources = ["aws_codebuild_project"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        artifacts = conf.get("artifacts")
        if not artifacts:
            return CheckResult.UNKNOWN

        artifacts = force_list(artifacts)[0]
        if isinstance(artifacts, dict):
            self.evaluated_keys.append("artifacts/[0]/type")
            if artifacts["type"] == ["NO_ARTIFACTS"]:
                # if a CodeBuild project does not define any artifacts,
                # then they also don't need to be encrypted
                return CheckResult.UNKNOWN

        self.evaluated_keys.append("encryption_key")
        if "encryption_key" in conf:
            return CheckResult.PASSED

        return CheckResult.FAILED


check = CodeBuildEncrypted()

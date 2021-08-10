from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class CodeBuildProjectEncryption(BaseResourceCheck):

    def __init__(self):
        name = "Ensure that CodeBuild Project encryption is not disabled"
        id = "CKV_AWS_78"
        supported_resources = ['aws_codebuild_project']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'artifacts' not in conf:
            return CheckResult.UNKNOWN
        artifact = conf['artifacts'][0]
        if isinstance(artifact, dict):
            if artifact['type'] == ["NO_ARTIFACTS"]:
                self.evaluated_keys = 'artifacts/[0]/type'
                return CheckResult.UNKNOWN
            if 'encryption_disabled' in artifact:   
                if artifact['encryption_disabled'] == [True]:
                   self.evaluated_keys = 'artifacts/[0]/encryption_disabled'
                   return CheckResult.FAILED
        return CheckResult.PASSED


check = CodeBuildProjectEncryption()

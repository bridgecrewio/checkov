from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class APIGatewayAuthorization(BaseResourceCheck):

    def __init__(self):
        name = "Ensure that CodeBuild Project encryption is not disabled"
        id = "CKV_AWS_78"
        supported_resources = ['aws_codebuild_project']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        artifact = conf['artifacts'][0]
        if isinstance(artifact, dict) and artifact['type'] != "NO_ARTIFACTS" and 'encryption_disabled' in artifact and artifact['encryption_disabled']:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = APIGatewayAuthorization()

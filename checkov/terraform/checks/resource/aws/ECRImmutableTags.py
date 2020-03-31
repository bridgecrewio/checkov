from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class ECRImmutableTags(BaseResourceCheck):
    def __init__(self):
        name = "Ensure ECR Image Tags are immutable"
        id = "CKV_AWS_51"
        supported_resources = ['aws_ecr_repository']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        key="image_tag_mutability"
        if key in conf.keys():
            if conf[key] == ['IMMUTABLE']:
                return CheckResult.PASSED
            else:
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED


check = ECRImmutableTags()

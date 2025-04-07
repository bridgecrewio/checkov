from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class S3EnvironmentCheck(BaseResourceCheck):
    def __init__(self):
        name = "Ensure s3 has environment tag of development/staging/production"
        id = "CUSTOM_AWS_2"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("tags") and isinstance(conf['tags'][0], dict):
            env = conf["tags"][0].get("Environment",{})
            if env in ["Development","Staging","Production"]:
                return CheckResult.PASSED
        return CheckResult.FAILED


scanner = S3EnvironmentCheck()

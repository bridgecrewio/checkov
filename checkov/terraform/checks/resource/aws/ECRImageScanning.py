from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class ECRImageScanning(BaseResourceCheck):
    def __init__(self):
        name = "Ensure ECR image scanning on push is enabled"
        id = "CKV_AWS_33"
        supported_resources = ['aws_ecr_repository']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for image scanning configuration at repository policy:
            https://www.terraform.io/docs/providers/aws/r/ecr_repository.html
        :param conf: aws_ecr_repository configuration
        :return: <CheckResult>
        """
        if "image_scanning_configuration" in conf.keys():
            if conf["image_scanning_configuration"][0]["scan_on_push"][0] == True:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = ECRImageScanning()

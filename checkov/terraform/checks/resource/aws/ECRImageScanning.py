from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class ECRImageScanning(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure ECR image scanning on push is enabled"
        id = "CKV_AWS_163"
        supported_resources = ['aws_ecr_repository']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "image_scanning_configuration/[0]/scan_on_push"

check = ECRImageScanning()

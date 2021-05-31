from checkov.common.models.enums import CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ECRImageScanning(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure ECR image scanning on push is enabled"
        id = "CKV_AWS_163"
        supported_resources = ["AWS::ECR::Repository"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "Properties/ImageScanningConfiguration/ScanOnPush"


check = ECRImageScanning()

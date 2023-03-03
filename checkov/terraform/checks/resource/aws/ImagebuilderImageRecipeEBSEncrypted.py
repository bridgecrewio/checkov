from typing import Dict, List, Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class ImagebuilderImageRecipeEBSEncrypted(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Image Recipe EBS Disk are encrypted with CMK"
        id = "CKV_AWS_200"
        supported_resources = ("aws_imagebuilder_image_recipe",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        mappings = conf.get("block_device_mapping")
        if mappings and isinstance(mappings, list):
            for mapping in mappings:
                if mapping.get("ebs"):
                    ebs = mapping["ebs"][0]
                    if not ebs.get("encrypted"):
                        return CheckResult.FAILED
                    if not ebs.get("kms_key_id"):
                        return CheckResult.FAILED
        # pass through
        return CheckResult.PASSED


check = ImagebuilderImageRecipeEBSEncrypted()

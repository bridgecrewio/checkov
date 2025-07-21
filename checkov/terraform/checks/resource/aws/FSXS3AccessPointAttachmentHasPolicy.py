from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class FSXS3AccessPointAttachmentHasPolicy(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure FSx for OpenZFS S3 Access Point Attachment has a policy"
        id = "CKV_AWS_395"
        supported_resources = ("aws_fsx_s3_access_point_attachment",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if conf.get("s3_access_point") and conf.get("s3_access_point")[0].get("policy"):
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> list[str]:
        return ["s3_access_point/[0]/policy"]


check = FSXS3AccessPointAttachmentHasPolicy()

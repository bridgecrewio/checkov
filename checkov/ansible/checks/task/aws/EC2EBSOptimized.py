from __future__ import annotations

from typing import Any

from checkov.ansible.checks.base_ansible_task_check import BaseAnsibleTaskCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.yaml_doc.enums import BlockType


class EC2EBSOptimized(BaseAnsibleTaskCheck):
    def __init__(self) -> None:
        name = "Ensure that EC2 is EBS optimized"
        id = "CKV_AWS_135"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.GENERAL_SECURITY,),
            supported_modules=("amazon.aws.ec2_instance",),
            block_type=BlockType.ARRAY,
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        if not conf.get("image_id") and not conf.get("image"):
            # if 'image_id' or 'image' are not set, then an already running instance is targeted
            return CheckResult.UNKNOWN, self.entity_conf

        if conf.get("ebs_optimized"):
            return CheckResult.PASSED, self.entity_conf

        return CheckResult.FAILED, self.entity_conf


check = EC2EBSOptimized()

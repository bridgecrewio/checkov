from __future__ import annotations

from typing import Any

from checkov.ansible.checks.base_ansible_task_value_check import BaseAnsibleTaskValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class EC2EBSOptimized(BaseAnsibleTaskValueCheck):
    def __init__(self) -> None:
        name = "Ensure that EC2 is EBS optimized"
        id = "CKV_AWS_135"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.GENERAL_SECURITY,),
            supported_modules=("amazon.aws.ec2_instance", "ec2_instance"),
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        if not conf.get("image_id") and not conf.get("image"):
            # if 'image_id' or 'image' are not set, then an already running instance is targeted
            return CheckResult.UNKNOWN, self.entity_conf

        return super().scan_conf(conf=conf)

    def get_inspected_key(self) -> str:
        return "ebs_optimized"


check = EC2EBSOptimized()

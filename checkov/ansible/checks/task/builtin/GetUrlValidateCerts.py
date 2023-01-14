from __future__ import annotations

from typing import Any

from checkov.ansible.checks.base_ansible_task_check import BaseAnsibleTaskCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.yaml_doc.enums import BlockType


class GetUrlValidateCerts(BaseAnsibleTaskCheck):
    def __init__(self) -> None:
        name = "Ensure that certificate validation isn't disabled with get_url"
        id = "CKV_ANSIBLE_2"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.GENERAL_SECURITY,),
            supported_modules=("ansible.builtin.get_url", "get_url"),
            block_type=BlockType.ARRAY,
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        if conf.get("validate_certs") is False:
            # default is 'True'
            return CheckResult.FAILED, self.entity_conf

        return CheckResult.PASSED, self.entity_conf


check = GetUrlValidateCerts()

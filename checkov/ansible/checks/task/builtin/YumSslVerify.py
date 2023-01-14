from __future__ import annotations

from typing import Any

from checkov.ansible.checks.base_ansible_task_check import BaseAnsibleTaskCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.yaml_doc.enums import BlockType


class YumSslVerify(BaseAnsibleTaskCheck):
    def __init__(self) -> None:
        name = "Ensure that SSL validation isn't disabled with yum"
        id = "CKV_ANSIBLE_4"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.GENERAL_SECURITY,),
            supported_modules=("ansible.builtin.yum", "yum"),
            block_type=BlockType.ARRAY,
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        if conf.get("sslverify") is False:
            # default is 'True'
            return CheckResult.FAILED, self.entity_conf

        return CheckResult.PASSED, self.entity_conf


check = YumSslVerify()

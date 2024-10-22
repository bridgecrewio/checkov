from __future__ import annotations

from checkov.ansible.checks.base_ansible_task_value_check import BaseAnsibleTaskValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class YumSslVerify(BaseAnsibleTaskValueCheck):
    def __init__(self) -> None:
        name = "Ensure that SSL validation isn't disabled with yum"
        id = "CKV_ANSIBLE_4"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.GENERAL_SECURITY,),
            supported_modules=("ansible.builtin.yum", "yum"),
            missing_block_result=CheckResult.PASSED,
        )

    def get_inspected_key(self) -> str:
        return "sslverify"


check = YumSslVerify()

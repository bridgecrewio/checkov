from __future__ import annotations

from typing import Any

from checkov.ansible.checks.base_ansible_task_value_check import BaseAnsibleTaskValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class AptForce(BaseAnsibleTaskValueCheck):
    def __init__(self) -> None:
        name = "Ensure that packages with untrusted or missing signatures are not used"
        id = "CKV_ANSIBLE_6"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.GENERAL_SECURITY,),
            supported_modules=("ansible.builtin.apt", "apt"),
            missing_block_result=CheckResult.PASSED,
        )

    def get_expected_value(self) -> Any:
        return False

    def get_inspected_key(self) -> str:
        return "force"


check = AptForce()

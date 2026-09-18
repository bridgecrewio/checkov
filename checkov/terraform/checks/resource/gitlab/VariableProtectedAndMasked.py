from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class VariableProtectedAndMasked(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure GitLab CI/CD variables are protected and masked"
        id = "CKV_GLB_5"
        supported_resources = ["gitlab_project_variable", "gitlab_group_variable", "gitlab_instance_variable"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        protected = conf.get("protected")
        masked = conf.get("masked")
        protected_ok = isinstance(protected, list) and protected[0] is True
        masked_ok = isinstance(masked, list) and masked[0] is True
        if protected_ok and masked_ok:
            return CheckResult.PASSED
        self.evaluated_keys = [key for key, ok in (("protected", protected_ok), ("masked", masked_ok)) if not ok]
        return CheckResult.FAILED


check = VariableProtectedAndMasked()

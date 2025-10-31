from __future__ import annotations

import json
from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class BatchJobIsNotPrivileged(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Batch job does not define a privileged container"
        id = "CKV_AWS_210"
        supported_resources = ("aws_batch_job_definition",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        self.evaluated_keys = ["container_properties"]
        container_properties = conf.get("container_properties")
        if container_properties:
            if isinstance(container_properties[0], str):
                try:
                    container = json.loads(container_properties[0])
                except json.JSONDecodeError:
                    return CheckResult.UNKNOWN
            else:
                container = container_properties[0]
            if not isinstance(container, dict):
                return CheckResult.UNKNOWN
            if container.get("privileged"):
                self.evaluated_keys.append("container_properties/[0]/privileged")
                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = BatchJobIsNotPrivileged()
